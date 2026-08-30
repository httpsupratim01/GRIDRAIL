from django.db.models import Count, Sum
from django.db.models.functions import TruncDate, TruncMonth
from django.utils import timezone
from rest_framework.response import Response
from rest_framework.views import APIView

from accounts.models import User
from accounts.permissions import IsAdminRole
from bookings.models import Booking
from cancellations.models import Refund
from payments.models import Payment
from stations.models import Station
from trains.models import Train


class DashboardStatsView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        revenue = Payment.objects.filter(payment_status=Payment.Status.SUCCESSFUL).aggregate(total=Sum("amount"))["total"] or 0
        dashboard_date = request.query_params.get("date") or timezone.localdate()
        today_bookings = Booking.objects.filter(created_at__date=dashboard_date).count()
        return Response(
            {
                "total_users": User.objects.count(),
                "total_trains": Train.objects.count(),
                "total_stations": Station.objects.count(),
                "todays_bookings": today_bookings,
                "confirmed_tickets": Booking.objects.filter(booking_status=Booking.Status.CONFIRMED).count(),
                "cancelled_tickets": Booking.objects.filter(booking_status=Booking.Status.CANCELLED).count(),
                "revenue": revenue,
                "pending_refunds": Refund.objects.filter(refund_status=Refund.Status.PENDING).count(),
            }
        )


class ReportsView(APIView):
    permission_classes = [IsAdminRole]

    def get(self, request):
        daily_bookings = (
            Booking.objects.annotate(day=TruncDate("created_at"))
            .values("day")
            .annotate(count=Count("id"))
            .order_by("day")[:30]
        )
        monthly_revenue = (
            Payment.objects.filter(payment_status=Payment.Status.SUCCESSFUL)
            .annotate(month=TruncMonth("payment_date"))
            .values("month")
            .annotate(total=Sum("amount"))
            .order_by("month")[:12]
        )
        popular_routes = (
            Booking.objects.values("source__code", "destination__code")
            .annotate(count=Count("id"))
            .order_by("-count")[:10]
        )
        return Response(
            {
                "daily_bookings": list(daily_bookings),
                "monthly_revenue": list(monthly_revenue),
                "popular_routes": list(popular_routes),
                "cancellations": Booking.objects.values("booking_status").annotate(count=Count("id")),
            }
        )

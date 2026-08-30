from decimal import Decimal

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsAdminRole
from cancellations.models import Cancellation, Refund
from payments.models import Payment
from .models import Booking, SeatReservation
from .serializers import BookingCreateSerializer, BookingSerializer


class BookingViewSet(viewsets.ModelViewSet):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Booking.objects.select_related("user", "train", "source", "destination").prefetch_related(
            "passengers", "seat_reservations"
        )
        if self.request.user.role == "ADMIN":
            return qs
        return qs.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.action == "create":
            return BookingCreateSerializer
        return BookingSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data, context={"request": request})
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["get"], url_path="pnr/(?P<pnr>[^/.]+)")
    def by_pnr(self, request, pnr=None):
        booking = get_object_or_404(self.get_queryset(), pnr=pnr)
        return Response(BookingSerializer(booking).data)

    @action(detail=True, methods=["post"], url_path="cancel")
    def cancel(self, request, pk=None):
        booking = self.get_object()
        if booking.booking_status == Booking.Status.CANCELLED:
            return Response({"detail": "Ticket is already cancelled."}, status=status.HTTP_400_BAD_REQUEST)
        reason = request.data.get("reason", "")
        with transaction.atomic():
            booking.booking_status = Booking.Status.CANCELLED
            booking.save(update_fields=["booking_status"])
            SeatReservation.objects.filter(booking=booking).delete()
            refund_amount = booking.total_fare * self._refund_rate(request)
            cancellation, _ = Cancellation.objects.update_or_create(
                booking=booking,
                defaults={"cancellation_reason": reason, "refund_amount": refund_amount},
            )
            payment = getattr(booking, "payment", None)
            if payment:
                payment.payment_status = Payment.Status.REFUNDED
                payment.save(update_fields=["payment_status"])
                Refund.objects.update_or_create(
                    booking=booking,
                    defaults={"payment": payment, "refund_amount": refund_amount, "refund_status": Refund.Status.PENDING},
                )
        return Response({"booking": BookingSerializer(booking).data, "cancellation_id": cancellation.id})

    def _refund_rate(self, request):
        configured = request.data.get("refund_rate")
        try:
            rate = Decimal(str(configured)) if configured is not None else Decimal("0.75")
        except ValueError:
            rate = Decimal("0.75")
        return max(Decimal("0"), min(Decimal("1"), rate))

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAdminRole()]
        return super().get_permissions()

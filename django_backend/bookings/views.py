from decimal import Decimal

from django.conf import settings
from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from accounts.permissions import IsAdminRole
from cancellations.models import Cancellation, Refund
from payments.gateway import create_razorpay_order, verify_razorpay_signature
from payments.models import Payment, PaymentOrder
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

    @action(detail=False, methods=["post"], url_path="razorpay-order")
    def razorpay_order(self, request):
        payload = request.data.copy()
        payload["payment_method"] = Payment.Method.RAZORPAY
        serializer = BookingCreateSerializer(data=payload, context={"request": request})
        serializer.is_valid(raise_exception=True)
        fare = serializer.validated_data["fare"]
        amount = fare.total_per_passenger * Decimal(len(serializer.validated_data["passengers"]))
        provider_order = create_razorpay_order(amount, receipt=f"GRIDRAIL-{request.user.id}")
        order = PaymentOrder.objects.create(
            user=request.user,
            provider_order_id=provider_order["id"],
            amount=amount,
            currency=provider_order.get("currency", "INR"),
            booking_payload=payload,
        )
        return Response(
            {
                "order_id": order.provider_order_id,
                "amount": provider_order["amount"],
                "currency": order.currency,
                "key_id": settings.RAZORPAY_KEY_ID,
                "name": "GRIDRAIL",
                "description": "Train ticket booking",
            },
            status=status.HTTP_201_CREATED,
        )

    @action(detail=False, methods=["post"], url_path="razorpay-confirm")
    def razorpay_confirm(self, request):
        order_id = request.data.get("razorpay_order_id")
        payment_id = request.data.get("razorpay_payment_id")
        signature = request.data.get("razorpay_signature")
        if not order_id or not payment_id or not signature:
            return Response({"detail": "Razorpay order id, payment id, and signature are required."}, status=status.HTTP_400_BAD_REQUEST)

        order = get_object_or_404(PaymentOrder, provider_order_id=order_id, user=request.user)
        if order.booking:
            return Response(BookingSerializer(order.booking).data)

        verify_razorpay_signature(order_id, payment_id, signature)
        payload = dict(order.booking_payload)
        payload["payment_method"] = Payment.Method.RAZORPAY
        serializer = BookingCreateSerializer(data=payload, context={"request": request})
        serializer.is_valid(raise_exception=True)
        booking = serializer.save()
        payment = booking.payment
        payment.transaction_id = payment_id
        payment.payment_method = Payment.Method.RAZORPAY
        payment.payment_status = Payment.Status.SUCCESSFUL
        payment.gateway_order_id = order_id
        payment.gateway_payment_id = payment_id
        payment.gateway_signature = signature
        payment.save()
        order.booking = booking
        order.status = PaymentOrder.Status.PAID
        order.save(update_fields=["booking", "status"])
        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)

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

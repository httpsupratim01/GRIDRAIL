import random

from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Payment
from .serializers import PaymentSerializer


class PaymentViewSet(viewsets.ModelViewSet):
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        qs = Payment.objects.select_related("booking", "booking__user")
        if self.request.user.role == "ADMIN":
            return qs
        return qs.filter(booking__user=self.request.user)

    @action(detail=False, methods=["post"], url_path="create")
    def create_payment(self, request):
        booking_id = request.data["booking"]
        amount = request.data["amount"]
        payment = Payment.objects.create(
            booking_id=booking_id,
            transaction_id=f"TXN{random.randint(1000000000, 9999999999)}",
            payment_method=request.data.get("payment_method", Payment.Method.UPI),
            amount=amount,
            payment_status=Payment.Status.PENDING,
        )
        return Response(PaymentSerializer(payment).data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=["post"], url_path="process")
    def process(self, request):
        payment = self.get_queryset().get(id=request.data["payment_id"])
        force_fail = request.data.get("force_fail", False)
        payment.payment_status = Payment.Status.FAILED if force_fail else Payment.Status.SUCCESSFUL
        if not payment.transaction_id:
            payment.transaction_id = f"TXN{random.randint(1000000000, 9999999999)}"
        payment.save()
        return Response(PaymentSerializer(payment).data, status=status.HTTP_200_OK)

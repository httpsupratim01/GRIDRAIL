from django.utils import timezone
from rest_framework import viewsets

from accounts.permissions import IsAdminRole
from .models import Cancellation, Refund
from .serializers import CancellationSerializer, RefundSerializer


class CancellationViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = CancellationSerializer

    def get_queryset(self):
        qs = Cancellation.objects.select_related("booking", "booking__user")
        if self.request.user.role == "ADMIN":
            return qs
        return qs.filter(booking__user=self.request.user)


class RefundViewSet(viewsets.ModelViewSet):
    serializer_class = RefundSerializer

    def get_queryset(self):
        qs = Refund.objects.select_related("booking", "payment", "booking__user")
        if self.request.user.role == "ADMIN":
            return qs
        return qs.filter(booking__user=self.request.user)

    def get_permissions(self):
        if self.action in ["update", "partial_update", "destroy"]:
            return [IsAdminRole()]
        return super().get_permissions()

    def perform_update(self, serializer):
        if serializer.validated_data.get("refund_status") == Refund.Status.PROCESSED:
            serializer.save(refund_date=timezone.now())
        else:
            serializer.save()

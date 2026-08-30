from rest_framework import serializers

from .models import Cancellation, Refund


class CancellationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Cancellation
        fields = "__all__"


class RefundSerializer(serializers.ModelSerializer):
    class Meta:
        model = Refund
        fields = "__all__"

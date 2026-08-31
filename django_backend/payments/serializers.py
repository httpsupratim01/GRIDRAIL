from rest_framework import serializers

from .models import Payment


class PaymentSerializer(serializers.ModelSerializer):
    pnr = serializers.CharField(source="booking.pnr", read_only=True)
    train_number = serializers.CharField(source="booking.train.train_number", read_only=True)
    train_name = serializers.CharField(source="booking.train.train_name", read_only=True)
    journey_date = serializers.DateField(source="booking.journey_date", read_only=True)

    class Meta:
        model = Payment
        fields = "__all__"
        read_only_fields = ["transaction_id", "payment_date"]

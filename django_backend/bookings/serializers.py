import random
from decimal import Decimal

from django.db import IntegrityError, transaction
from rest_framework import serializers

from payments.models import Payment
from trains.models import Fare, Seat
from .models import Booking, Passenger, SeatReservation


def generate_pnr():
    while True:
        pnr = "".join(str(random.randint(0, 9)) for _ in range(10))
        if not Booking.objects.filter(pnr=pnr).exists():
            return pnr


class PassengerSerializer(serializers.ModelSerializer):
    class Meta:
        model = Passenger
        fields = "__all__"
        read_only_fields = ["booking"]


class SeatReservationSerializer(serializers.ModelSerializer):
    seat_number = serializers.IntegerField(source="seat.seat_number", read_only=True)
    coach_number = serializers.CharField(source="coach.coach_number", read_only=True)

    class Meta:
        model = SeatReservation
        fields = "__all__"


class BookingSerializer(serializers.ModelSerializer):
    passengers = PassengerSerializer(many=True, read_only=True)
    seat_reservations = SeatReservationSerializer(many=True, read_only=True)
    payment_status = serializers.CharField(source="payment.payment_status", read_only=True)
    train_name = serializers.CharField(source="train.train_name", read_only=True)
    train_number = serializers.CharField(source="train.train_number", read_only=True)
    source_code = serializers.CharField(source="source.code", read_only=True)
    destination_code = serializers.CharField(source="destination.code", read_only=True)

    class Meta:
        model = Booking
        fields = "__all__"
        read_only_fields = ["pnr", "user", "total_fare", "booking_status", "created_at"]


class BookingCreateSerializer(serializers.Serializer):
    train = serializers.IntegerField()
    journey_date = serializers.DateField()
    source = serializers.IntegerField()
    destination = serializers.IntegerField()
    class_type = serializers.CharField()
    payment_method = serializers.ChoiceField(choices=Payment.Method.choices)
    passengers = PassengerSerializer(many=True)
    seat_ids = serializers.ListField(child=serializers.IntegerField(), min_length=1)

    def validate(self, attrs):
        if len(attrs["passengers"]) != len(attrs["seat_ids"]):
            raise serializers.ValidationError("Passenger count must match selected seats.")
        fare = Fare.objects.filter(train_id=attrs["train"], class_type=attrs["class_type"]).first()
        if not fare:
            raise serializers.ValidationError("Fare is not configured for the selected train and class.")
        attrs["fare"] = fare
        return attrs

    def create(self, validated_data):
        request = self.context["request"]
        passenger_rows = validated_data.pop("passengers")
        seat_ids = validated_data.pop("seat_ids")
        fare = validated_data.pop("fare")
        journey_date = validated_data["journey_date"]
        total = fare.total_per_passenger * Decimal(len(passenger_rows))

        try:
            with transaction.atomic():
                seats = list(
                    Seat.objects.select_for_update()
                    .select_related("coach", "coach__train")
                    .filter(id__in=seat_ids, coach__train_id=validated_data["train"], coach__class_type=validated_data["class_type"])
                )
                if len(seats) != len(seat_ids):
                    raise serializers.ValidationError("One or more selected seats are invalid for this train and class.")
                booked = SeatReservation.objects.filter(seat_id__in=seat_ids, journey_date=journey_date).exists()
                if booked:
                    raise serializers.ValidationError("One or more selected seats were just booked. Please choose different seats.")

                booking = Booking.objects.create(
                    pnr=generate_pnr(),
                    user=request.user,
                    train_id=validated_data["train"],
                    journey_date=journey_date,
                    source_id=validated_data["source"],
                    destination_id=validated_data["destination"],
                    class_type=validated_data["class_type"],
                    total_fare=total,
                )
                for passenger_data, seat in zip(passenger_rows, seats):
                    passenger = Passenger.objects.create(booking=booking, **passenger_data)
                    SeatReservation.objects.create(
                        booking=booking,
                        passenger=passenger,
                        seat=seat,
                        coach=seat.coach,
                        journey_date=journey_date,
                    )
                Payment.objects.create(
                    booking=booking,
                    transaction_id=f"TXN{random.randint(1000000000, 9999999999)}",
                    payment_method=validated_data["payment_method"],
                    amount=total,
                    payment_status=Payment.Status.SUCCESSFUL,
                )
                return booking
        except IntegrityError as exc:
            raise serializers.ValidationError("Selected seat is no longer available.") from exc

from rest_framework import serializers

from stations.serializers import StationSerializer
from .models import Coach, Fare, Route, Seat, Train


class RouteSerializer(serializers.ModelSerializer):
    station_detail = StationSerializer(source="station", read_only=True)

    class Meta:
        model = Route
        fields = "__all__"


class SeatSerializer(serializers.ModelSerializer):
    class Meta:
        model = Seat
        fields = "__all__"


class CoachSerializer(serializers.ModelSerializer):
    seats = SeatSerializer(many=True, read_only=True)

    class Meta:
        model = Coach
        fields = "__all__"


class FareSerializer(serializers.ModelSerializer):
    total_per_passenger = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Fare
        fields = "__all__"


class TrainSerializer(serializers.ModelSerializer):
    source_station_detail = StationSerializer(source="source_station", read_only=True)
    destination_station_detail = StationSerializer(source="destination_station", read_only=True)
    routes = RouteSerializer(many=True, read_only=True)
    coaches = CoachSerializer(many=True, read_only=True)
    fares = FareSerializer(many=True, read_only=True)

    class Meta:
        model = Train
        fields = "__all__"

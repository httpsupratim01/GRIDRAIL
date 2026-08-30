from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticatedOrReadOnly
from rest_framework.response import Response

from accounts.permissions import IsAdminRole
from bookings.models import SeatReservation
from .models import Coach, Fare, Route, Seat, Train
from .serializers import CoachSerializer, FareSerializer, RouteSerializer, SeatSerializer, TrainSerializer


class AdminMutationMixin:
    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminRole()]
        return [IsAuthenticatedOrReadOnly()]


class TrainViewSet(AdminMutationMixin, viewsets.ModelViewSet):
    queryset = Train.objects.select_related("source_station", "destination_station").prefetch_related("routes", "coaches", "fares")
    serializer_class = TrainSerializer
    search_fields = ["train_number", "train_name", "train_type"]

    @action(detail=True, methods=["get"], url_path="availability")
    def availability(self, request, pk=None):
        train = self.get_object()
        journey_date = request.query_params.get("journey_date")
        class_type = request.query_params.get("class_type")
        coaches = train.coaches.all()
        if class_type:
            coaches = coaches.filter(class_type=class_type)
        reserved = set(
            SeatReservation.objects.filter(
                coach__train=train, journey_date=journey_date
            ).values_list("seat_id", flat=True)
            if journey_date
            else []
        )
        payload = []
        for coach in coaches.prefetch_related("seats"):
            seats = [
                {
                    "id": seat.id,
                    "seat_number": seat.seat_number,
                    "seat_type": seat.seat_type,
                    "status": "BOOKED" if seat.id in reserved else seat.status,
                }
                for seat in coach.seats.all()
            ]
            payload.append({"coach": CoachSerializer(coach).data, "seats": seats})
        return Response(payload)

    @action(detail=True, methods=["get"], url_path="schedule")
    def schedule(self, request, pk=None):
        return Response(RouteSerializer(self.get_object().routes.all(), many=True).data)


class RouteViewSet(AdminMutationMixin, viewsets.ModelViewSet):
    queryset = Route.objects.select_related("train", "station")
    serializer_class = RouteSerializer


class CoachViewSet(AdminMutationMixin, viewsets.ModelViewSet):
    queryset = Coach.objects.select_related("train").prefetch_related("seats")
    serializer_class = CoachSerializer


class SeatViewSet(AdminMutationMixin, viewsets.ModelViewSet):
    queryset = Seat.objects.select_related("coach", "coach__train")
    serializer_class = SeatSerializer


class FareViewSet(AdminMutationMixin, viewsets.ModelViewSet):
    queryset = Fare.objects.select_related("train")
    serializer_class = FareSerializer

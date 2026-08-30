from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from accounts.permissions import IsAdminRole
from .models import Station
from .serializers import StationSerializer


class StationViewSet(viewsets.ModelViewSet):
    queryset = Station.objects.all()
    serializer_class = StationSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    search_fields = ["name", "code", "city", "state"]

    def get_permissions(self):
        if self.action in ["create", "update", "partial_update", "destroy"]:
            return [IsAdminRole()]
        return super().get_permissions()

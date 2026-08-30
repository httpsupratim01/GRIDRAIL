from django.db import models


class Train(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"
        MAINTENANCE = "MAINTENANCE", "Maintenance"

    train_number = models.CharField(max_length=20, unique=True)
    train_name = models.CharField(max_length=140)
    train_type = models.CharField(max_length=60, db_index=True)
    source_station = models.ForeignKey("stations.Station", on_delete=models.PROTECT, related_name="source_trains")
    destination_station = models.ForeignKey("stations.Station", on_delete=models.PROTECT, related_name="destination_trains")
    running_days = models.JSONField(default=list)
    distance = models.PositiveIntegerField(default=0)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, db_index=True)

    class Meta:
        ordering = ["train_number"]
        indexes = [models.Index(fields=["train_type", "status"])]

    def __str__(self):
        return f"{self.train_number} - {self.train_name}"


class Route(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name="routes")
    station = models.ForeignKey("stations.Station", on_delete=models.PROTECT, related_name="route_stops")
    sequence = models.PositiveIntegerField()
    arrival_time = models.TimeField(null=True, blank=True)
    departure_time = models.TimeField(null=True, blank=True)
    halt_minutes = models.PositiveIntegerField(default=0)
    distance_from_source = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ["train", "sequence"]
        constraints = [
            models.UniqueConstraint(fields=["train", "sequence"], name="unique_train_route_sequence"),
            models.UniqueConstraint(fields=["train", "station"], name="unique_train_route_station"),
        ]

    def __str__(self):
        return f"{self.train.train_number} stop {self.sequence}: {self.station.code}"


class Coach(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"

    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name="coaches")
    coach_number = models.CharField(max_length=12)
    coach_type = models.CharField(max_length=40, db_index=True)
    class_type = models.CharField(max_length=20, db_index=True)
    total_seats = models.PositiveIntegerField()
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE)

    class Meta:
        ordering = ["train", "coach_number"]
        constraints = [models.UniqueConstraint(fields=["train", "coach_number"], name="unique_train_coach")]

    def __str__(self):
        return f"{self.train.train_number} {self.coach_number}"


class Seat(models.Model):
    class Status(models.TextChoices):
        AVAILABLE = "AVAILABLE", "Available"
        RESERVED = "RESERVED", "Reserved"
        BLOCKED = "BLOCKED", "Blocked"

    coach = models.ForeignKey(Coach, on_delete=models.CASCADE, related_name="seats")
    seat_number = models.PositiveIntegerField()
    seat_type = models.CharField(max_length=40, default="Window")
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.AVAILABLE, db_index=True)

    class Meta:
        ordering = ["coach", "seat_number"]
        constraints = [models.UniqueConstraint(fields=["coach", "seat_number"], name="unique_coach_seat")]

    def __str__(self):
        return f"{self.coach.coach_number}-{self.seat_number}"


class Fare(models.Model):
    train = models.ForeignKey(Train, on_delete=models.CASCADE, related_name="fares")
    class_type = models.CharField(max_length=20)
    base_fare = models.DecimalField(max_digits=10, decimal_places=2)
    reservation_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    service_charge = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    class Meta:
        ordering = ["train", "class_type"]
        constraints = [models.UniqueConstraint(fields=["train", "class_type"], name="unique_train_class_fare")]

    @property
    def total_per_passenger(self):
        return self.base_fare + self.reservation_charge + self.service_charge

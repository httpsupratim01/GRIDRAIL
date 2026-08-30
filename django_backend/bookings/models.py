from django.conf import settings
from django.db import models


class Booking(models.Model):
    class Status(models.TextChoices):
        CONFIRMED = "CONFIRMED", "Confirmed"
        RAC = "RAC", "RAC"
        WAITING = "WAITING", "Waiting"
        CANCELLED = "CANCELLED", "Cancelled"
        COMPLETED = "COMPLETED", "Completed"

    pnr = models.CharField(max_length=10, unique=True, db_index=True)
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="bookings")
    train = models.ForeignKey("trains.Train", on_delete=models.PROTECT, related_name="bookings")
    journey_date = models.DateField(db_index=True)
    source = models.ForeignKey("stations.Station", on_delete=models.PROTECT, related_name="departing_bookings")
    destination = models.ForeignKey("stations.Station", on_delete=models.PROTECT, related_name="arriving_bookings")
    class_type = models.CharField(max_length=20, db_index=True)
    total_fare = models.DecimalField(max_digits=10, decimal_places=2)
    booking_status = models.CharField(max_length=20, choices=Status.choices, default=Status.CONFIRMED, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        indexes = [models.Index(fields=["user", "journey_date"]), models.Index(fields=["train", "journey_date"])]

    def __str__(self):
        return self.pnr


class Passenger(models.Model):
    class Gender(models.TextChoices):
        MALE = "MALE", "Male"
        FEMALE = "FEMALE", "Female"
        OTHER = "OTHER", "Other"

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="passengers")
    name = models.CharField(max_length=120)
    age = models.PositiveIntegerField()
    gender = models.CharField(max_length=20, choices=Gender.choices)
    phone = models.CharField(max_length=20)
    email = models.EmailField(blank=True)
    id_type = models.CharField(max_length=40)
    id_number = models.CharField(max_length=80)
    seat_preference = models.CharField(max_length=40, blank=True)
    meal_preference = models.CharField(max_length=40, blank=True)

    def __str__(self):
        return self.name


class SeatReservation(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name="seat_reservations")
    passenger = models.OneToOneField(Passenger, on_delete=models.CASCADE, related_name="seat_reservation")
    seat = models.ForeignKey("trains.Seat", on_delete=models.PROTECT, related_name="reservations")
    coach = models.ForeignKey("trains.Coach", on_delete=models.PROTECT, related_name="reservations")
    journey_date = models.DateField(db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [models.UniqueConstraint(fields=["seat", "journey_date"], name="unique_seat_per_journey_date")]
        indexes = [models.Index(fields=["coach", "journey_date"])]

    def __str__(self):
        return f"{self.booking.pnr}: {self.seat}"

from datetime import date, timedelta

from django.contrib.auth import get_user_model
from django.test import TestCase
from rest_framework.test import APIClient

from accounts.management.commands.seed_demo import Command
from bookings.models import SeatReservation
from trains.models import Seat, Train


class RailwayFlowTests(TestCase):
    def setUp(self):
        Command().handle()
        self.client = APIClient()
        response = self.client.post("/api/auth/login", {"email": "passenger@railway.test", "password": "Passenger@12345"})
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {response.data['access']}")

    def test_registration_and_login(self):
        User = get_user_model()
        self.assertTrue(User.objects.filter(email="passenger@railway.test").exists())

    def test_booking_prevents_duplicate_seat(self):
        train = Train.objects.get(train_number="12952")
        seat = Seat.objects.filter(coach__train=train, coach__class_type="Sleeper").exclude(reservations__isnull=False).first()
        payload = {
            "train": train.id,
            "journey_date": str(date.today() + timedelta(days=10)),
            "source": train.source_station_id,
            "destination": train.destination_station_id,
            "class_type": "Sleeper",
            "payment_method": "UPI",
            "seat_ids": [seat.id],
            "passengers": [
                {
                    "name": "Test Passenger",
                    "age": 30,
                    "gender": "MALE",
                    "phone": "9000000000",
                    "email": "test@example.com",
                    "id_type": "Aadhaar",
                    "id_number": "1111",
                }
            ],
        }
        first = self.client.post("/api/bookings/", payload, format="json")
        second = self.client.post("/api/bookings/", payload, format="json")
        self.assertEqual(first.status_code, 201)
        self.assertEqual(second.status_code, 400)
        self.assertEqual(SeatReservation.objects.filter(seat=seat, journey_date=payload["journey_date"]).count(), 1)

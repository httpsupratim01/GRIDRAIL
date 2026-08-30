import os
from datetime import date, time, timedelta
from decimal import Decimal

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand

from bookings.models import Booking, Passenger, SeatReservation
from payments.models import Payment
from stations.models import Station
from trains.models import Coach, Fare, Route, Seat, Train


class Command(BaseCommand):
    help = "Seed demo railway reservation data."

    def handle(self, *args, **options):
        User = get_user_model()
        admin_username = os.getenv("ADMIN_USERNAME", "tanuja")
        admin_email = os.getenv("ADMIN_EMAIL", "tanuja@gridrail.test")
        admin_password = os.getenv("ADMIN_PASSWORD", "Tanuja@123")
        passenger_username = os.getenv("PASSENGER_USERNAME", "supratim")
        passenger_email = os.getenv("PASSENGER_EMAIL", "supratim@gridrail.test")
        passenger_password = os.getenv("PASSENGER_PASSWORD", "Supratim@123")

        User.objects.update_or_create(
            email=admin_email,
            defaults={
                "username": admin_username,
                "role": "ADMIN",
                "is_staff": True,
                "is_superuser": True,
                "phone": "9000000001",
                "avatar_url": "https://images.unsplash.com/photo-1494790108377-be9c29b29330?auto=format&fit=crop&w=320&q=80",
            },
        )
        admin = User.objects.get(email=admin_email)
        admin.set_password(admin_password)
        admin.save()

        passenger, _ = User.objects.update_or_create(
            email=passenger_email,
            defaults={
                "username": passenger_username,
                "role": "PASSENGER",
                "phone": "9876543210",
                "address": "Kolkata, West Bengal",
                "avatar_url": "https://images.unsplash.com/photo-1500648767791-00dcc994a43e?auto=format&fit=crop&w=320&q=80",
                "frequent_journeys": ["NDLS-MMCT", "SBC-NDLS", "HWH-GHY"],
            },
        )
        passenger.set_password(passenger_password)
        passenger.save()

        station_rows = [
            ("New Delhi", "NDLS", "New Delhi", "Delhi", "Northern"),
            ("Mumbai Central", "MMCT", "Mumbai", "Maharashtra", "Western"),
            ("Howrah Junction", "HWH", "Kolkata", "West Bengal", "Eastern"),
            ("Chennai Central", "MAS", "Chennai", "Tamil Nadu", "Southern"),
            ("Bengaluru City", "SBC", "Bengaluru", "Karnataka", "South Western"),
            ("Hyderabad Deccan", "HYB", "Hyderabad", "Telangana", "South Central"),
            ("Pune Junction", "PUNE", "Pune", "Maharashtra", "Central"),
            ("Ahmedabad Junction", "ADI", "Ahmedabad", "Gujarat", "Western"),
            ("Jaipur Junction", "JP", "Jaipur", "Rajasthan", "North Western"),
            ("Lucknow NR", "LKO", "Lucknow", "Uttar Pradesh", "Northern"),
            ("Patna Junction", "PNBE", "Patna", "Bihar", "East Central"),
            ("Bhopal Junction", "BPL", "Bhopal", "Madhya Pradesh", "West Central"),
            ("Kolkata Sealdah", "SDAH", "Kolkata", "West Bengal", "Eastern"),
            ("Kanpur Central", "CNB", "Kanpur", "Uttar Pradesh", "North Central"),
            ("Nagpur Junction", "NGP", "Nagpur", "Maharashtra", "Central"),
            ("Surat", "ST", "Surat", "Gujarat", "Western"),
            ("Vadodara Junction", "BRC", "Vadodara", "Gujarat", "Western"),
            ("Visakhapatnam", "VSKP", "Visakhapatnam", "Andhra Pradesh", "East Coast"),
            ("Guwahati", "GHY", "Guwahati", "Assam", "Northeast Frontier"),
            ("Thiruvananthapuram Central", "TVC", "Thiruvananthapuram", "Kerala", "Southern"),
            ("Coimbatore Junction", "CBE", "Coimbatore", "Tamil Nadu", "Southern"),
            ("Indore Junction", "INDB", "Indore", "Madhya Pradesh", "Western"),
            ("Varanasi Junction", "BSB", "Varanasi", "Uttar Pradesh", "Northern"),
            ("Ranchi Junction", "RNC", "Ranchi", "Jharkhand", "South Eastern"),
        ]
        stations = {}
        for name, code, city, state, zone in station_rows:
            station, _ = Station.objects.update_or_create(
                code=code,
                defaults={"name": name, "city": city, "state": state, "zone": zone, "status": "ACTIVE"},
            )
            stations[code] = station

        train_rows = [
            ("12952", "Mumbai Rajdhani Express", "Rajdhani", "NDLS", "MMCT", 1384),
            ("12002", "Shatabdi Express", "Shatabdi", "NDLS", "BPL", 707),
            ("12295", "Sanghamitra Express", "Superfast", "SBC", "PNBE", 2690),
            ("12627", "Karnataka Express", "Superfast", "SBC", "NDLS", 2406),
            ("12840", "Chennai Howrah Mail", "Mail", "MAS", "HWH", 1663),
            ("12723", "Telangana Express", "Superfast", "HYB", "NDLS", 1677),
            ("12957", "Swarna Jayanti Rajdhani", "Rajdhani", "ADI", "NDLS", 934),
            ("12985", "Jaipur Double Decker", "Double Decker", "JP", "NDLS", 303),
            ("12124", "Deccan Queen", "Intercity", "PUNE", "MMCT", 192),
            ("12309", "Rajendra Nagar Tejas", "Tejas", "PNBE", "NDLS", 1001),
        ]
        city_pairs = [
            ("NDLS", "MMCT"), ("NDLS", "HWH"), ("NDLS", "MAS"), ("NDLS", "SBC"), ("NDLS", "HYB"),
            ("MMCT", "MAS"), ("MMCT", "HWH"), ("MMCT", "JP"), ("MMCT", "ADI"), ("MMCT", "PUNE"),
            ("SBC", "PNBE"), ("SBC", "NDLS"), ("SBC", "TVC"), ("SBC", "CBE"), ("SBC", "HYB"),
            ("MAS", "HWH"), ("MAS", "VSKP"), ("MAS", "TVC"), ("MAS", "CBE"), ("MAS", "SBC"),
            ("HYB", "NDLS"), ("HYB", "PUNE"), ("HYB", "NGP"), ("HYB", "VSKP"), ("HYB", "BPL"),
            ("ADI", "NDLS"), ("ADI", "JP"), ("ADI", "BRC"), ("ADI", "ST"), ("ADI", "MMCT"),
            ("JP", "NDLS"), ("JP", "LKO"), ("JP", "BPL"), ("JP", "INDB"), ("JP", "ADI"),
            ("PNBE", "NDLS"), ("PNBE", "HWH"), ("PNBE", "BSB"), ("PNBE", "RNC"), ("PNBE", "GHY"),
            ("HWH", "GHY"), ("HWH", "RNC"), ("HWH", "VSKP"), ("HWH", "MAS"), ("HWH", "SDAH"),
            ("PUNE", "NGP"), ("PUNE", "BPL"), ("PUNE", "HYB"), ("PUNE", "MMCT"), ("PUNE", "BRC"),
        ]
        train_types = ["Superfast", "Express", "Intercity", "Mail", "Rajdhani", "Shatabdi", "Duronto", "Tejas"]
        train_names = [
            "GRIDRAIL Northern Link", "GRIDRAIL Coastal Express", "GRIDRAIL Metro Connect", "GRIDRAIL Valley Rider",
            "GRIDRAIL Heritage Mail", "GRIDRAIL Diamond Express", "GRIDRAIL Sunrise Superfast", "GRIDRAIL Nightline",
            "GRIDRAIL Central Star", "GRIDRAIL Junction Runner", "GRIDRAIL Cityline", "GRIDRAIL Deccan Flyer",
        ]
        while len(train_rows) < 100:
            idx = len(train_rows)
            src, dst = city_pairs[idx % len(city_pairs)]
            distance = 220 + ((idx * 137) % 2500)
            train_rows.append(
                (
                    str(13000 + idx),
                    f"{train_names[idx % len(train_names)]} {idx + 1:03d}",
                    train_types[idx % len(train_types)],
                    src,
                    dst,
                    distance,
                )
            )

        for idx, (number, name, typ, src, dst, distance) in enumerate(train_rows):
            train, _ = Train.objects.update_or_create(
                train_number=number,
                defaults={
                    "train_name": name,
                    "train_type": typ,
                    "source_station": stations[src],
                    "destination_station": stations[dst],
                    "running_days": ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"] if idx % 2 == 0 else ["Mon", "Wed", "Fri", "Sun"],
                    "distance": distance,
                    "status": "ACTIVE",
                },
            )
            midpoint_codes = ["BPL", "JP", "LKO", "PUNE", "HYB", "NGP", "BRC", "BSB", "RNC", "VSKP"]
            route_codes = list(dict.fromkeys([src, midpoint_codes[idx % len(midpoint_codes)], dst]))
            for sequence, code in enumerate(route_codes, start=1):
                Route.objects.update_or_create(
                    train=train,
                    sequence=sequence,
                    defaults={
                        "station": stations[code],
                        "arrival_time": None if sequence == 1 else time((6 + sequence * 4 + idx) % 24, 15),
                        "departure_time": None if sequence == len(route_codes) else time((6 + sequence * 4 + idx) % 24, 30),
                        "halt_minutes": 10 if 1 < sequence < len(route_codes) else 0,
                        "distance_from_source": int(distance * (sequence - 1) / (len(route_codes) - 1)),
                    },
                )
            for class_type, coach_number, coach_type, total in [
                ("1A", "A1", "AC First Class", 12),
                ("2A", "A2", "AC Two Tier", 18),
                ("3A", "B1", "AC Three Tier", 24),
                ("Sleeper", "S1", "Sleeper", 32),
                ("Chair Car", "C1", "Chair Car", 24),
                ("General", "G1", "General", 32),
            ]:
                coach, _ = Coach.objects.update_or_create(
                    train=train,
                    coach_number=coach_number,
                    defaults={"coach_type": coach_type, "class_type": class_type, "total_seats": total, "status": "ACTIVE"},
                )
                for seat_number in range(1, total + 1):
                    Seat.objects.update_or_create(
                        coach=coach,
                        seat_number=seat_number,
                        defaults={"seat_type": "Window" if seat_number % 6 in [1, 0] else "Aisle", "status": "AVAILABLE"},
                    )
                Fare.objects.update_or_create(
                    train=train,
                    class_type=class_type,
                    defaults={
                        "base_fare": Decimal(distance) * Decimal({"1A": "3.8", "2A": "2.6", "3A": "1.8", "Sleeper": "0.75", "Chair Car": "1.2", "General": "0.35"}[class_type]),
                        "reservation_charge": Decimal("40.00"),
                        "service_charge": Decimal("25.00"),
                    },
                )

        train = Train.objects.get(train_number="12952")
        fare = Fare.objects.get(train=train, class_type="Sleeper")
        if not Booking.objects.filter(pnr="4827319056").exists():
            booking = Booking.objects.create(
                pnr="4827319056",
                user=passenger,
                train=train,
                journey_date=date.today() + timedelta(days=7),
                source=train.source_station,
                destination=train.destination_station,
                class_type="Sleeper",
                total_fare=fare.total_per_passenger,
            )
            passenger_row = Passenger.objects.create(
                booking=booking,
                name="Aarav Sharma",
                age=28,
                gender="MALE",
                phone="9876543210",
                email=passenger.email,
                id_type="Aadhaar",
                id_number="XXXX-XXXX-1234",
                seat_preference="Window",
            )
            seat = Seat.objects.filter(coach__train=train, coach__class_type="Sleeper").first()
            SeatReservation.objects.create(
                booking=booking,
                passenger=passenger_row,
                seat=seat,
                coach=seat.coach,
                journey_date=booking.journey_date,
            )
            Payment.objects.create(
                booking=booking,
                transaction_id="TXN4827319056",
                payment_method="UPI",
                amount=booking.total_fare,
                payment_status="SUCCESSFUL",
            )

        self.stdout.write(self.style.SUCCESS("Demo railway data seeded."))

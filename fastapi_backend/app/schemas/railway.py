from datetime import date
from decimal import Decimal
from typing import Optional

from pydantic import BaseModel


class TrainSearchResult(BaseModel):
    train_id: int
    train_number: str
    train_name: str
    train_type: str
    departure_station: str
    arrival_station: str
    departure_time: Optional[str]
    arrival_time: Optional[str]
    duration: str
    available_classes: list[str]
    available_seats: int
    fare: Decimal
    train_status: str


class SeatState(BaseModel):
    id: int
    coach_number: str
    seat_number: int
    seat_type: str
    status: str


class FareQuote(BaseModel):
    train_id: int
    class_type: str
    passengers: int
    base_fare: Decimal
    reservation_charge: Decimal
    service_charge: Decimal
    total_fare: Decimal


class PnrLookup(BaseModel):
    pnr: str
    journey_date: date
    class_type: str
    total_fare: Decimal
    booking_status: str

from datetime import date
from decimal import Decimal

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.models.railway import Booking, Coach, Fare, Route, Seat, SeatReservation, Station, Train


def search_trains(db: Session, source: str, destination: str, journey_date: date, class_type: str | None, passengers: int):
    source = source.upper()
    destination = destination.upper()
    trains = (
        db.query(Train)
        .join(Station, Train.source_station_id == Station.id)
        .filter(Train.status == "ACTIVE")
        .all()
    )
    results = []
    for train in trains:
        stops = db.query(Route).filter(Route.train_id == train.id).order_by(Route.sequence).all()
        codes = [db.get(Station, stop.station_id).code for stop in stops]
        if source not in codes or destination not in codes or codes.index(source) >= codes.index(destination):
            continue
        fares = db.query(Fare).filter(Fare.train_id == train.id).all()
        classes = [fare.class_type for fare in fares]
        wanted_class = class_type or (classes[0] if classes else "")
        if class_type and class_type not in classes:
            continue
        available = available_seat_count(db, train.id, journey_date, wanted_class)
        if available < passengers:
            continue
        source_stop = stops[codes.index(source)]
        destination_stop = stops[codes.index(destination)]
        fare = next((item for item in fares if item.class_type == wanted_class), None)
        results.append(
            {
                "train_id": train.id,
                "train_number": train.train_number,
                "train_name": train.train_name,
                "train_type": train.train_type,
                "departure_station": source,
                "arrival_station": destination,
                "departure_time": str(source_stop.departure_time) if source_stop.departure_time else None,
                "arrival_time": str(destination_stop.arrival_time) if destination_stop.arrival_time else None,
                "duration": f"{max(1, destination_stop.sequence - source_stop.sequence) * 4}h {30 + train.id % 20}m",
                "available_classes": classes,
                "available_seats": available,
                "fare": fare.base_fare + fare.reservation_charge + fare.service_charge if fare else Decimal("0"),
                "train_status": train.status,
            }
        )
    return results


def available_seat_count(db: Session, train_id: int, journey_date: date, class_type: str):
    total = (
        db.query(func.count(Seat.id))
        .join(Coach, Seat.coach_id == Coach.id)
        .filter(Coach.train_id == train_id, Coach.class_type == class_type, Seat.status == "AVAILABLE")
        .scalar()
    )
    booked = (
        db.query(func.count(SeatReservation.id))
        .join(Coach, SeatReservation.coach_id == Coach.id)
        .filter(Coach.train_id == train_id, Coach.class_type == class_type, SeatReservation.journey_date == journey_date)
        .scalar()
    )
    return int((total or 0) - (booked or 0))


def seat_map(db: Session, train_id: int, journey_date: date, class_type: str):
    booked = {
        row[0]
        for row in db.query(SeatReservation.seat_id)
        .join(Coach, SeatReservation.coach_id == Coach.id)
        .filter(Coach.train_id == train_id, Coach.class_type == class_type, SeatReservation.journey_date == journey_date)
    }
    seats = (
        db.query(Seat, Coach)
        .join(Coach, Seat.coach_id == Coach.id)
        .filter(Coach.train_id == train_id, Coach.class_type == class_type)
        .order_by(Coach.coach_number, Seat.seat_number)
        .all()
    )
    return [
        {
            "id": seat.id,
            "coach_number": coach.coach_number,
            "seat_number": seat.seat_number,
            "seat_type": seat.seat_type,
            "status": "BOOKED" if seat.id in booked else seat.status,
        }
        for seat, coach in seats
    ]

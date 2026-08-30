from sqlalchemy import Column, Date, DateTime, ForeignKey, Integer, Numeric, String, Time
from sqlalchemy.orm import relationship

from app.database.session import Base


class Station(Base):
    __tablename__ = "stations_station"

    id = Column(Integer, primary_key=True)
    name = Column(String)
    code = Column(String)
    city = Column(String)
    state = Column(String)
    zone = Column(String)
    status = Column(String)


class Train(Base):
    __tablename__ = "trains_train"

    id = Column(Integer, primary_key=True)
    train_number = Column(String)
    train_name = Column(String)
    train_type = Column(String)
    source_station_id = Column(Integer, ForeignKey("stations_station.id"))
    destination_station_id = Column(Integer, ForeignKey("stations_station.id"))
    running_days = Column(String)
    distance = Column(Integer)
    status = Column(String)
    source_station = relationship("Station", foreign_keys=[source_station_id])
    destination_station = relationship("Station", foreign_keys=[destination_station_id])


class Route(Base):
    __tablename__ = "trains_route"

    id = Column(Integer, primary_key=True)
    train_id = Column(Integer, ForeignKey("trains_train.id"))
    station_id = Column(Integer, ForeignKey("stations_station.id"))
    sequence = Column(Integer)
    arrival_time = Column(Time)
    departure_time = Column(Time)
    halt_minutes = Column(Integer)
    distance_from_source = Column(Integer)
    station = relationship("Station")


class Coach(Base):
    __tablename__ = "trains_coach"

    id = Column(Integer, primary_key=True)
    train_id = Column(Integer, ForeignKey("trains_train.id"))
    coach_number = Column(String)
    coach_type = Column(String)
    class_type = Column(String)
    total_seats = Column(Integer)
    status = Column(String)


class Seat(Base):
    __tablename__ = "trains_seat"

    id = Column(Integer, primary_key=True)
    coach_id = Column(Integer, ForeignKey("trains_coach.id"))
    seat_number = Column(Integer)
    seat_type = Column(String)
    status = Column(String)


class Fare(Base):
    __tablename__ = "trains_fare"

    id = Column(Integer, primary_key=True)
    train_id = Column(Integer, ForeignKey("trains_train.id"))
    class_type = Column(String)
    base_fare = Column(Numeric)
    reservation_charge = Column(Numeric)
    service_charge = Column(Numeric)


class Booking(Base):
    __tablename__ = "bookings_booking"

    id = Column(Integer, primary_key=True)
    pnr = Column(String)
    user_id = Column(Integer)
    train_id = Column(Integer, ForeignKey("trains_train.id"))
    journey_date = Column(Date)
    source_id = Column(Integer, ForeignKey("stations_station.id"))
    destination_id = Column(Integer, ForeignKey("stations_station.id"))
    class_type = Column(String)
    total_fare = Column(Numeric)
    booking_status = Column(String)
    created_at = Column(DateTime)


class SeatReservation(Base):
    __tablename__ = "bookings_seatreservation"

    id = Column(Integer, primary_key=True)
    booking_id = Column(Integer, ForeignKey("bookings_booking.id"))
    passenger_id = Column(Integer)
    seat_id = Column(Integer, ForeignKey("trains_seat.id"))
    coach_id = Column(Integer, ForeignKey("trains_coach.id"))
    journey_date = Column(Date)

from datetime import date

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session

from app.database.session import get_db
from app.models.railway import Booking, Fare, Route, Station, Train
from app.schemas.railway import FareQuote, PnrLookup, SeatState, TrainSearchResult
from app.services.search import search_trains, seat_map

router = APIRouter(prefix="/api", tags=["railway"])


@router.get("/search/trains", response_model=list[TrainSearchResult])
def train_search(
    source: str = Query(..., description="Source station code, e.g. NDLS"),
    destination: str = Query(..., description="Destination station code, e.g. MMCT"),
    journey_date: date = Query(...),
    class_type: str | None = None,
    passengers: int = Query(1, ge=1, le=6),
    sort_by: str = "departure_time",
    db: Session = Depends(get_db),
):
    results = search_trains(db, source, destination, journey_date, class_type, passengers)
    if sort_by in {"fare", "available_seats", "departure_time", "arrival_time", "duration"}:
        results = sorted(results, key=lambda item: item.get(sort_by) or "")
    return results


@router.get("/trains/{train_id}/availability", response_model=list[SeatState])
def availability(train_id: int, journey_date: date, class_type: str, db: Session = Depends(get_db)):
    if not db.get(Train, train_id):
        raise HTTPException(status_code=404, detail="Train not found")
    return seat_map(db, train_id, journey_date, class_type)


@router.get("/trains/{train_id}/schedule")
def schedule(train_id: int, db: Session = Depends(get_db)):
    rows = db.query(Route).filter(Route.train_id == train_id).order_by(Route.sequence).all()
    return [
        {
            "sequence": row.sequence,
            "station": db.get(Station, row.station_id).code,
            "arrival_time": str(row.arrival_time) if row.arrival_time else None,
            "departure_time": str(row.departure_time) if row.departure_time else None,
            "halt_minutes": row.halt_minutes,
            "distance_from_source": row.distance_from_source,
        }
        for row in rows
    ]


@router.get("/fares/calculate", response_model=FareQuote)
def calculate_fare(train_id: int, class_type: str, passengers: int = Query(1, ge=1, le=6), db: Session = Depends(get_db)):
    fare = db.query(Fare).filter(Fare.train_id == train_id, Fare.class_type == class_type).first()
    if not fare:
        raise HTTPException(status_code=404, detail="Fare not configured")
    per_passenger = fare.base_fare + fare.reservation_charge + fare.service_charge
    return {
        "train_id": train_id,
        "class_type": class_type,
        "passengers": passengers,
        "base_fare": fare.base_fare,
        "reservation_charge": fare.reservation_charge,
        "service_charge": fare.service_charge,
        "total_fare": per_passenger * passengers,
    }


@router.get("/bookings/pnr/{pnr}", response_model=PnrLookup)
def pnr_lookup(pnr: str, db: Session = Depends(get_db)):
    booking = db.query(Booking).filter(Booking.pnr == pnr).first()
    if not booking:
        raise HTTPException(status_code=404, detail="Invalid PNR")
    return booking


@router.get("/analytics/occupancy")
def occupancy(db: Session = Depends(get_db)):
    trains = db.query(Train).all()
    return [
        {
            "train_number": train.train_number,
            "train_name": train.train_name,
            "bookings": db.query(Booking).filter(Booking.train_id == train.id).count(),
        }
        for train in trains
    ]

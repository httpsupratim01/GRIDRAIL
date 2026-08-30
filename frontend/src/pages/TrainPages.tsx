import { useEffect, useMemo, useState } from "react";
import { Link, useLocation, useNavigate, useParams, useSearchParams } from "react-router-dom";
import SearchWidget from "../components/SearchWidget";
import { djangoApi, fastApi } from "../services/api";
import { currency } from "../utils/format";

type TrainResult = {
  train_id: number;
  train_number: string;
  train_name: string;
  train_type: string;
  departure_station: string;
  arrival_station: string;
  departure_time: string;
  arrival_time: string;
  duration: string;
  available_classes: string[];
  available_seats: number;
  fare: string;
  train_status: string;
};

type Seat = { id: number; coach_number: string; seat_number: number; seat_type: string; status: string };

export function TrainSearchPage() {
  return (
    <section className="page-card">
      <h1>Search Trains</h1>
      <SearchWidget compact />
    </section>
  );
}

export function TrainResultsPage() {
  const [params, setParams] = useSearchParams();
  const [trains, setTrains] = useState<TrainResult[]>([]);
  const [loading, setLoading] = useState(true);
  const navigate = useNavigate();

  useEffect(() => {
    setLoading(true);
    fastApi
      .get("/search/trains", { params: Object.fromEntries(params) })
      .then(({ data }) => setTrains(data))
      .finally(() => setLoading(false));
  }, [params]);

  function sortBy(sort_by: string) {
    params.set("sort_by", sort_by);
    setParams(params);
  }

  return (
    <section className="page-card">
      <div className="section-title">
        <h1>Train Results</h1>
        <select onChange={(e) => sortBy(e.target.value)} defaultValue="departure_time">
          <option value="departure_time">Departure time</option>
          <option value="arrival_time">Arrival time</option>
          <option value="duration">Duration</option>
          <option value="fare">Fare</option>
          <option value="available_seats">Availability</option>
        </select>
      </div>
      {loading && <p>Loading trains...</p>}
      {!loading && trains.length === 0 && <p className="empty">No trains found for this route and class.</p>}
      <div className="train-list">
        {trains.map((train) => (
          <article className="train-row" key={train.train_id}>
            <div>
              <strong>{train.train_number} · {train.train_name}</strong>
              <span>{train.train_type} · {train.departure_station} {train.departure_time} → {train.arrival_station} {train.arrival_time}</span>
            </div>
            <div>
              <strong>{train.duration}</strong>
              <span>{train.available_seats} seats · {currency(train.fare)}</span>
            </div>
            <button onClick={() => navigate(`/trains/${train.train_id}?${params.toString()}`)}>View Details</button>
            <button className="primary-action" onClick={() => navigate(`/availability/${train.train_id}?${params.toString()}`)}>Book Now</button>
          </article>
        ))}
      </div>
    </section>
  );
}

export function TrainDetailsPage() {
  const { id } = useParams();
  const [train, setTrain] = useState<any>();
  useEffect(() => {
    djangoApi.get(`/trains/${id}/`).then(({ data }) => setTrain(data));
  }, [id]);
  if (!train) return <section className="page-card">Loading train details...</section>;
  return (
    <section className="page-card">
      <h1>{train.train_number} · {train.train_name}</h1>
      <div className="metrics">
        <span>{train.train_type}</span><span>{train.distance} km</span><span>{train.status}</span>
      </div>
      <h2>Complete Route</h2>
      <table><tbody>{train.routes.map((stop: any) => <tr key={stop.id}><td>{stop.sequence}</td><td>{stop.station_detail.code}</td><td>{stop.arrival_time || "Origin"}</td><td>{stop.departure_time || "Terminus"}</td><td>{stop.distance_from_source} km</td></tr>)}</tbody></table>
      <h2>Fare by Class</h2>
      <div className="fare-grid">{train.fares.map((fare: any) => <span key={fare.id}>{fare.class_type}: {currency(fare.total_per_passenger)}</span>)}</div>
    </section>
  );
}

export function SeatAvailabilityPage() {
  const { id } = useParams();
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const [seats, setSeats] = useState<Seat[]>([]);
  const [selected, setSelected] = useState<number[]>([]);
  const passengers = Number(params.get("passengers") || 1);
  useEffect(() => {
    fastApi.get(`/trains/${id}/availability`, { params: { journey_date: params.get("journey_date"), class_type: params.get("class_type") } }).then(({ data }) => setSeats(data));
  }, [id, params]);
  function toggle(seat: Seat) {
    if (seat.status !== "AVAILABLE") return;
    setSelected((current) => current.includes(seat.id) ? current.filter((item) => item !== seat.id) : current.length < passengers ? [...current, seat.id] : current);
  }
  return (
    <section className="page-card">
      <h1>Seat Availability</h1>
      <div className="seat-map">
        {seats.map((seat) => (
          <button key={seat.id} className={`seat ${seat.status.toLowerCase()} ${selected.includes(seat.id) ? "selected" : ""}`} onClick={() => toggle(seat)}>
            {seat.coach_number}-{seat.seat_number}
          </button>
        ))}
      </div>
      <button className="primary-action" disabled={selected.length !== passengers} onClick={() => navigate(`/passenger-details/${id}?${params.toString()}&seat_ids=${selected.join(",")}`)}>
        Continue with {selected.length}/{passengers} seats
      </button>
    </section>
  );
}

export function PassengerDetailsPage() {
  const { id } = useParams();
  const [params] = useSearchParams();
  const navigate = useNavigate();
  const count = Number(params.get("passengers") || 1);
  const [passengers, setPassengers] = useState(Array.from({ length: count }, () => ({ name: "", age: 25, gender: "MALE", phone: "", email: "", id_type: "Aadhaar", id_number: "", seat_preference: "Window", meal_preference: "" })));
  function update(index: number, key: string, value: string | number) {
    setPassengers((rows) => rows.map((row, i) => (i === index ? { ...row, [key]: value } : row)));
  }
  return (
    <section className="page-card">
      <h1>Passenger Details</h1>
      {passengers.map((person, index) => (
        <div className="form-grid" key={index}>
          <input placeholder="Name" value={person.name} onChange={(e) => update(index, "name", e.target.value)} />
          <input type="number" placeholder="Age" value={person.age} onChange={(e) => update(index, "age", Number(e.target.value))} />
          <select value={person.gender} onChange={(e) => update(index, "gender", e.target.value)}><option>MALE</option><option>FEMALE</option><option>OTHER</option></select>
          <input placeholder="Mobile" value={person.phone} onChange={(e) => update(index, "phone", e.target.value)} />
          <input placeholder="Email" value={person.email} onChange={(e) => update(index, "email", e.target.value)} />
          <input placeholder="ID number" value={person.id_number} onChange={(e) => update(index, "id_number", e.target.value)} />
        </div>
      ))}
      <button className="primary-action" onClick={() => navigate(`/review/${id}?${params.toString()}`, { state: { passengers } })}>Review Booking</button>
    </section>
  );
}

export function BookingReviewPage() {
  const { id } = useParams();
  const [params] = useSearchParams();
  const location = useLocation();
  const navigate = useNavigate();
  const passengers = Number(params.get("passengers") || 1);
  const [quote, setQuote] = useState<any>();
  useEffect(() => {
    fastApi.get("/fares/calculate", { params: { train_id: id, class_type: params.get("class_type"), passengers } }).then(({ data }) => setQuote(data));
  }, [id, params, passengers]);
  return (
    <section className="page-card">
      <h1>Booking Review</h1>
      <p>{params.get("source")} → {params.get("destination")} on {params.get("journey_date")}</p>
      {quote && <p>Total fare: <strong>{currency(quote.total_fare)}</strong></p>}
      <button className="primary-action" onClick={() => navigate(`/payment/${id}?${params.toString()}`, { state: location.state })}>Proceed to Payment</button>
    </section>
  );
}

export function PaymentPage() {
  const { id } = useParams();
  const [params] = useSearchParams();
  const location = useLocation();
  const navigate = useNavigate();
  const [method, setMethod] = useState("UPI");
  async function pay() {
    const passengerCount = Number(params.get("passengers") || 1);
    const stationResponse = await djangoApi.get("/stations/");
    const stations = stationResponse.data.results || stationResponse.data;
    const source = stations.find((station: any) => station.code === params.get("source"));
    const destination = stations.find((station: any) => station.code === params.get("destination"));
    if (!source || !destination) throw new Error("Invalid station selection");
    const payload = {
      train: Number(id),
      journey_date: params.get("journey_date"),
      source: source.id,
      destination: destination.id,
      class_type: params.get("class_type"),
      payment_method: method,
      seat_ids: (params.get("seat_ids") || "").split(",").map(Number),
      passengers: location.state?.passengers || Array.from({ length: passengerCount }, (_, index) => ({ name: `Passenger ${index + 1}`, age: 30, gender: "MALE", phone: "9000000000", email: "passenger@example.com", id_type: "Aadhaar", id_number: `DEMO-${index + 1}` }))
    };
    const { data } = await djangoApi.post("/bookings/", payload);
    navigate(`/confirmation/${data.id}`);
  }
  return (
    <section className="page-card">
      <h1>Simulated Payment</h1>
      <select value={method} onChange={(e) => setMethod(e.target.value)}><option>UPI</option><option>CREDIT_CARD</option><option>DEBIT_CARD</option><option>NET_BANKING</option></select>
      <input placeholder="Dummy payment detail" />
      <button className="primary-action" onClick={pay}>Process Payment</button>
    </section>
  );
}

export function ConfirmationPage() {
  const { id } = useParams();
  const [booking, setBooking] = useState<any>();
  useEffect(() => { djangoApi.get(`/bookings/${id}/`).then(({ data }) => setBooking(data)); }, [id]);
  if (!booking) return <section className="page-card">Confirming...</section>;
  return <section className="page-card"><h1>Booking Confirmed</h1><p>PNR: <strong>{booking.pnr}</strong></p><Link className="primary-action" to={`/tickets/${booking.id}`}>Open E-Ticket</Link></section>;
}

export function MyBookingsPage() {
  const [bookings, setBookings] = useState<any[]>([]);
  useEffect(() => { djangoApi.get("/bookings/").then(({ data }) => setBookings(data.results || data)); }, []);
  return (
    <section className="page-card">
      <h1>My Bookings</h1>
      <table><tbody>{bookings.map((b) => <tr key={b.id}><td>{b.pnr}</td><td>{b.train_number}</td><td>{b.journey_date}</td><td>{b.booking_status}</td><td><Link to={`/tickets/${b.id}`}>Ticket</Link></td><td><Link to={`/cancel/${b.id}`}>Cancel</Link></td></tr>)}</tbody></table>
    </section>
  );
}

export function TicketDetailsPage() {
  const { id } = useParams();
  const [booking, setBooking] = useState<any>();
  useEffect(() => { djangoApi.get(`/bookings/${id}/`).then(({ data }) => setBooking(data)); }, [id]);
  const seats = useMemo(() => booking?.seat_reservations?.map((s: any) => `${s.coach_number}-${s.seat_number}`).join(", "), [booking]);
  if (!booking) return <section className="page-card">Loading ticket...</section>;
  return <section className="ticket"><h1>GRIDRAIL E-Ticket</h1><p>PNR {booking.pnr}</p><p>{booking.train_number} · {booking.train_name}</p><p>{booking.source_code} → {booking.destination_code} · {booking.journey_date}</p><p>Seats: {seats}</p><p>Fare: {currency(booking.total_fare)} · {booking.payment_status}</p><button onClick={() => window.print()}>Print / Download Ticket</button></section>;
}

export function CancellationPage() {
  const { id } = useParams();
  const navigate = useNavigate();
  async function cancel() {
    await djangoApi.post(`/bookings/${id}/cancel/`, { reason: "Passenger requested cancellation", refund_rate: 0.75 });
    navigate("/refunds");
  }
  return <section className="page-card"><h1>Cancel Ticket</h1><p>Cancellation policy: confirmed tickets receive a configurable refund. Seats are released after cancellation.</p><button className="danger" onClick={cancel}>Confirm Cancellation</button></section>;
}

export function RefundStatusPage() {
  const [refunds, setRefunds] = useState<any[]>([]);
  useEffect(() => { djangoApi.get("/refunds/").then(({ data }) => setRefunds(data.results || data)); }, []);
  return <section className="page-card"><h1>Refund Status</h1><table><tbody>{refunds.map((r) => <tr key={r.id}><td>{currency(r.refund_amount)}</td><td>{r.refund_status}</td><td>{r.refund_date || "Pending"}</td></tr>)}</tbody></table></section>;
}

import { useEffect, useMemo, useState } from "react";
import { Ban, CalendarDays, CreditCard, Landmark, MapPin, Smartphone, Ticket, TicketCheck, TrainFront, UserRound, WalletCards } from "lucide-react";
import { Link, useLocation, useNavigate, useParams, useSearchParams } from "react-router-dom";
import SearchWidget from "../components/SearchWidget";
import { useAuth } from "../context/AuthContext";
import { djangoApi, fastApi } from "../services/api";
import { currency } from "../utils/format";

declare global {
  interface Window {
    Razorpay?: new (options: Record<string, unknown>) => { open: () => void };
  }
}

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

type Booking = {
  id: number;
  pnr: string;
  train_number: string;
  train_name?: string;
  source_code: string;
  destination_code: string;
  journey_date: string;
  class_type: string;
  total_fare: string;
  booking_status: string;
  payment_status?: string;
  seat_reservations?: { coach_number: string; seat_number: number }[];
};

type PassengerForm = {
  name: string;
  age: number;
  gender: string;
  phone: string;
  email: string;
  id_type: string;
  id_number: string;
  seat_preference: string;
  meal_preference: string;
};

const paymentMethods = [
  ["UPI", "UPI", Smartphone],
  ["CREDIT_CARD", "Credit Card", CreditCard],
  ["DEBIT_CARD", "Debit Card", WalletCards],
  ["NET_BANKING", "Net Banking", Landmark],
] as const;

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
  const [passengers, setPassengers] = useState<PassengerForm[]>(Array.from({ length: count }, () => ({ name: "", age: 25, gender: "MALE", phone: "", email: "", id_type: "Aadhaar", id_number: "", seat_preference: "Window", meal_preference: "" })));
  const [error, setError] = useState("");
  function update(index: number, key: string, value: string | number) {
    setPassengers((rows) => rows.map((row, i) => (i === index ? { ...row, [key]: value } : row)));
  }
  function review() {
    const incomplete = passengers.some((person) => !person.name.trim() || !person.phone.trim() || !person.id_number.trim() || person.age < 1);
    if (incomplete) {
      setError("Enter name, valid age, mobile number, and ID number for every passenger.");
      return;
    }
    navigate(`/review/${id}?${params.toString()}`, { state: { passengers } });
  }
  return (
    <section className="page-card booking-step">
      <div className="section-title">
        <h1>Passenger Details</h1>
        <span>{count} traveller{count > 1 ? "s" : ""}</span>
      </div>
      {passengers.map((person, index) => (
        <article className="passenger-card" key={index}>
          <h2><UserRound size={18} /> Passenger {index + 1}</h2>
          <div className="form-grid">
            <label>Name<input placeholder="Full name" value={person.name} onChange={(e) => update(index, "name", e.target.value)} /></label>
            <label>Age<input type="number" min={1} max={120} placeholder="Age" value={person.age} onChange={(e) => update(index, "age", Number(e.target.value))} /></label>
            <label>Gender<select value={person.gender} onChange={(e) => update(index, "gender", e.target.value)}><option>MALE</option><option>FEMALE</option><option>OTHER</option></select></label>
            <label>Mobile<input placeholder="Mobile" value={person.phone} onChange={(e) => update(index, "phone", e.target.value)} /></label>
            <label>Email<input type="email" placeholder="Email optional" value={person.email} onChange={(e) => update(index, "email", e.target.value)} /></label>
            <label>ID Type<select value={person.id_type} onChange={(e) => update(index, "id_type", e.target.value)}><option>Aadhaar</option><option>PAN</option><option>Voter ID</option><option>Passport</option></select></label>
            <label>ID Number<input placeholder="ID number" value={person.id_number} onChange={(e) => update(index, "id_number", e.target.value)} /></label>
            <label>Seat Preference<select value={person.seat_preference} onChange={(e) => update(index, "seat_preference", e.target.value)}><option>Window</option><option>Aisle</option><option>Lower</option><option>Middle</option><option>Upper</option><option>No preference</option></select></label>
            <label>Meal Preference<select value={person.meal_preference} onChange={(e) => update(index, "meal_preference", e.target.value)}><option value="">No meal</option><option>Veg</option><option>Non-Veg</option><option>Jain</option></select></label>
          </div>
        </article>
      ))}
      {error && <p className="error">{error}</p>}
      <button className="primary-action" onClick={review}>Review Booking</button>
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
    <section className="page-card booking-step">
      <div className="section-title"><h1>Booking Review</h1><span>{params.get("class_type")} · {passengers} passenger{passengers > 1 ? "s" : ""}</span></div>
      <div className="review-grid">
        <article><span>Route</span><strong>{params.get("source")} to {params.get("destination")}</strong></article>
        <article><span>Journey Date</span><strong>{params.get("journey_date")}</strong></article>
        <article><span>Selected Seats</span><strong>{params.get("seat_ids")?.split(",").length || 0}</strong></article>
        <article><span>Total Fare</span><strong>{quote ? currency(quote.total_fare) : "Calculating"}</strong></article>
      </div>
      <div className="module-list">
        {(location.state?.passengers || []).map((person: PassengerForm, index: number) => (
          <article key={`${person.name}-${index}`}>
            <div><strong>{person.name}</strong><span>{person.gender} · {person.age} years · {person.id_type}</span></div>
            <small>Passenger {index + 1}</small>
          </article>
        ))}
      </div>
      <button className="primary-action" onClick={() => navigate(`/payment/${id}?${params.toString()}`, { state: location.state })}>Proceed to Payment</button>
    </section>
  );
}

export function PaymentPage() {
  const { id } = useParams();
  const [params] = useSearchParams();
  const location = useLocation();
  const navigate = useNavigate();
  const { user } = useAuth();
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState("");
  const passengerCount = Number(params.get("passengers") || 1);

  function bookingPayload() {
    return {
      train: Number(id),
      journey_date: params.get("journey_date"),
      source_code: params.get("source"),
      destination_code: params.get("destination"),
      class_type: params.get("class_type"),
      seat_ids: (params.get("seat_ids") || "").split(",").filter(Boolean).map(Number),
      passengers: location.state?.passengers || Array.from({ length: passengerCount }, (_, index) => ({ name: `Passenger ${index + 1}`, age: 30, gender: "MALE", phone: "9000000000", email: "passenger@example.com", id_type: "Aadhaar", id_number: `DEMO-${index + 1}` }))
    };
  }

  function loadRazorpayScript() {
    return new Promise<boolean>((resolve) => {
      if (window.Razorpay) {
        resolve(true);
        return;
      }
      const script = document.createElement("script");
      script.src = "https://checkout.razorpay.com/v1/checkout.js";
      script.onload = () => resolve(true);
      script.onerror = () => resolve(false);
      document.body.appendChild(script);
    });
  }

  async function pay() {
    setProcessing(true);
    setError("");
    try {
      const loaded = await loadRazorpayScript();
      if (!loaded || !window.Razorpay) {
        throw new Error("Razorpay checkout could not be loaded. Check your internet connection.");
      }
      const { data: order } = await djangoApi.post("/bookings/razorpay-order/", bookingPayload());
      const checkout = new window.Razorpay({
        key: order.key_id,
        amount: order.amount,
        currency: order.currency,
        name: order.name,
        description: order.description,
        order_id: order.order_id,
        prefill: {
          name: user?.username || "",
          email: user?.email || "",
          contact: user?.phone || "",
        },
        theme: { color: "#f45c2f" },
        handler: async (response: any) => {
          const { data: booking } = await djangoApi.post("/bookings/razorpay-confirm/", response);
          navigate(`/confirmation/${booking.id}`);
        },
        modal: {
          ondismiss: () => {
            setProcessing(false);
          },
        },
      });
      checkout.open();
    } catch (err: any) {
      setError(err.response?.data?.detail || err.response?.data?.non_field_errors?.[0] || err.message || "Payment could not be completed. Please try again.");
      setProcessing(false);
    }
  }
  return (
    <section className="page-card booking-step payment-step">
      <div className="section-title"><h1>Payment</h1><span>Razorpay checkout</span></div>
      <div className="payment-methods">
        {paymentMethods.map(([value, label, Icon]) => (
          <button type="button" key={value}>
            <Icon size={20} />
            {label}
          </button>
        ))}
      </div>
      <div className="payment-box">
        <p>Amount is calculated from selected train, class, seats, and passengers. Booking is confirmed only after Razorpay payment verification succeeds.</p>
      </div>
      {error && <p className="error">{error}</p>}
      <button className="primary-action" disabled={processing} onClick={pay}>{processing ? "Opening Razorpay..." : "Pay Securely with Razorpay"}</button>
    </section>
  );
}

export function ConfirmationPage() {
  const { id } = useParams();
  const [booking, setBooking] = useState<any>();
  useEffect(() => { djangoApi.get(`/bookings/${id}/`).then(({ data }) => setBooking(data)); }, [id]);
  if (!booking) return <section className="page-card">Confirming...</section>;
  return (
    <section className="page-card confirmation-card">
      <TicketCheck size={48} />
      <h1>Booking Confirmed</h1>
      <p>PNR: <strong>{booking.pnr}</strong></p>
      <p>{booking.train_number} · {booking.source_code} to {booking.destination_code} · {booking.journey_date}</p>
      <div className="confirmation-actions">
        <Link className="primary-action" to={`/tickets/${booking.id}`}>Open E-Ticket</Link>
        <Link className="secondary-action" to="/bookings">View My Bookings</Link>
      </div>
    </section>
  );
}

export function MyBookingsPage() {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    djangoApi.get("/bookings/")
      .then(({ data }) => setBookings(data.results || data))
      .finally(() => setLoading(false));
  }, []);
  const activeBookings = bookings.filter((booking) => booking.booking_status !== "CANCELLED");
  return (
    <section className="page-card booking-ledger">
      <div className="section-title">
        <div>
          <span className="eyebrow">Passenger Tickets</span>
          <h1>My Bookings</h1>
        </div>
        <Link className="secondary-action" to="/cancellations">Cancelled Tickets</Link>
      </div>
      <div className="ticket-summary">
        <article><Ticket size={18} /><span>Active</span><strong>{activeBookings.length}</strong></article>
        <article><Ban size={18} /><span>Cancelled</span><strong>{bookings.length - activeBookings.length}</strong></article>
      </div>
      {loading && <p>Loading bookings...</p>}
      {!loading && activeBookings.length === 0 && <p className="empty">No active bookings yet. Book a train and it will appear here.</p>}
      <div className="ticket-list">
        {activeBookings.map((booking) => <BookingCard key={booking.id} booking={booking} />)}
      </div>
    </section>
  );
}

export function CancelledTicketsPage() {
  const [bookings, setBookings] = useState<Booking[]>([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    djangoApi.get("/bookings/")
      .then(({ data }) => setBookings(data.results || data))
      .finally(() => setLoading(false));
  }, []);
  const cancelledBookings = bookings.filter((booking) => booking.booking_status === "CANCELLED");
  return (
    <section className="page-card booking-ledger">
      <div className="section-title">
        <div>
          <span className="eyebrow">Cancelled Section</span>
          <h1>Cancelled Tickets</h1>
        </div>
        <Link className="secondary-action" to="/bookings">Active Bookings</Link>
      </div>
      {loading && <p>Loading cancelled tickets...</p>}
      {!loading && cancelledBookings.length === 0 && <p className="empty">No cancelled tickets yet. Cancelled bookings will move here automatically.</p>}
      <div className="ticket-list">
        {cancelledBookings.map((booking) => <BookingCard key={booking.id} booking={booking} cancelled />)}
      </div>
    </section>
  );
}

function BookingCard({ booking, cancelled = false }: { booking: Booking; cancelled?: boolean }) {
  const seats = booking.seat_reservations?.map((seat) => `${seat.coach_number}-${seat.seat_number}`).join(", ") || "Assigned";
  return (
    <article className={`ticket-card ${cancelled ? "cancelled" : ""}`}>
      <div className="ticket-card-main">
        <div className="ticket-icon"><TrainFront size={22} /></div>
        <div>
          <strong>{booking.train_number} · {booking.train_name || "GRIDRAIL Express"}</strong>
          <span><MapPin size={14} /> {booking.source_code} to {booking.destination_code}</span>
        </div>
      </div>
      <div className="ticket-meta">
        <span><CalendarDays size={14} /> {booking.journey_date}</span>
        <span>{booking.class_type} · {seats}</span>
        <span>PNR {booking.pnr}</span>
      </div>
      <div className="ticket-actions">
        <small className={`status-pill ${cancelled ? "danger-pill" : ""}`}>{booking.booking_status}</small>
        <Link to={`/tickets/${booking.id}`}>Ticket</Link>
        {!cancelled && <Link className="danger-link" to={`/cancel/${booking.id}`}>Cancel</Link>}
      </div>
    </article>
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
  const [booking, setBooking] = useState<Booking>();
  const [reason, setReason] = useState("Passenger requested cancellation");
  const [processing, setProcessing] = useState(false);
  const [error, setError] = useState("");
  useEffect(() => { djangoApi.get(`/bookings/${id}/`).then(({ data }) => setBooking(data)); }, [id]);
  async function cancel() {
    setProcessing(true);
    setError("");
    try {
      await djangoApi.post(`/bookings/${id}/cancel/`, { reason, refund_rate: 0.75 });
      navigate("/cancellations");
    } catch (err: any) {
      setError(err.response?.data?.detail || "Ticket could not be cancelled.");
      setProcessing(false);
    }
  }
  if (!booking) return <section className="page-card">Loading ticket...</section>;
  return (
    <section className="page-card booking-ledger">
      <div className="section-title">
        <div>
          <span className="eyebrow">Cancel Ticket</span>
          <h1>PNR {booking.pnr}</h1>
        </div>
        <Link className="secondary-action" to="/bookings">Back to Bookings</Link>
      </div>
      <BookingCard booking={booking} />
      <div className="cancel-panel">
        <h2>Cancellation Details</h2>
        <p>After confirmation this ticket moves from My Bookings to Cancelled Tickets. Seats are released and refund status is created.</p>
        <label>Reason<textarea value={reason} onChange={(event) => setReason(event.target.value)} /></label>
        {error && <p className="error">{error}</p>}
        <button className="danger" disabled={processing || booking.booking_status === "CANCELLED"} onClick={cancel}>
          {processing ? "Cancelling..." : booking.booking_status === "CANCELLED" ? "Already Cancelled" : "Confirm Cancellation"}
        </button>
      </div>
    </section>
  );
}

export function RefundStatusPage() {
  const [refunds, setRefunds] = useState<any[]>([]);
  useEffect(() => { djangoApi.get("/refunds/").then(({ data }) => setRefunds(data.results || data)); }, []);
  return <section className="page-card"><h1>Refund Status</h1><table><tbody>{refunds.map((r) => <tr key={r.id}><td>{currency(r.refund_amount)}</td><td>{r.refund_status}</td><td>{r.refund_date || "Pending"}</td></tr>)}</tbody></table></section>;
}

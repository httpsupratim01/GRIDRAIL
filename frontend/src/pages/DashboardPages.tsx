import { ChangeEvent, useEffect, useRef, useState } from "react";
import { Bar, BarChart, CartesianGrid, Line, LineChart, ResponsiveContainer, Tooltip, XAxis, YAxis } from "recharts";
import SearchWidget from "../components/SearchWidget";
import { useAuth } from "../context/AuthContext";
import { djangoApi, fastApi } from "../services/api";
import { currency } from "../utils/format";

export function PassengerDashboard() {
  const { user } = useAuth();
  const [bookings, setBookings] = useState<any[]>([]);
  const [trains, setTrains] = useState<any[]>([]);
  useEffect(() => {
    djangoApi.get("/bookings/").then(({ data }) => setBookings(data.results || data));
    djangoApi.get("/trains/").then(({ data }) => setTrains(data.results || data));
  }, []);
  return (
    <section className="dashboard">
      <div className="profile-hero">
        <div className="profile-avatar">{user?.avatar_url ? <img src={user.avatar_url} alt="" /> : user?.username?.slice(0, 1).toUpperCase()}</div>
        <div>
          <span>Passenger Workspace</span>
          <h1>Welcome, {user?.username}</h1>
          <p>{user?.email}</p>
        </div>
      </div>
      <SearchWidget compact />
      <div className="stat-grid">
        <article><span>Total Trains</span><strong>{trains.length || 100}</strong></article>
        <article><span>My Bookings</span><strong>{bookings.length}</strong></article>
        <article><span>Saved Routes</span><strong>{user?.frequent_journeys?.length || 3}</strong></article>
      </div>
      <div className="module-grid">
        <article><h2>Saved Journeys</h2><p>{user?.frequent_journeys?.join(", ") || "NDLS-MMCT, SBC-NDLS, HWH-GHY"}</p></article>
        <article><h2>Travel Alerts</h2><p>Platform, coach, and refund updates are grouped in Alerts for quick scanning.</p></article>
        <article><h2>Quick PNR</h2><p>Open PNR Status to review ticket status, payment, and journey date.</p></article>
        <article><h2>Payments</h2><p>Track simulated UPI, card, and net banking payments from one module.</p></article>
      </div>
    </section>
  );
}

export function ProfilePage({ admin = false }: { admin?: boolean }) {
  const { user, refreshUser } = useAuth();
  const galleryInputRef = useRef<HTMLInputElement>(null);
  const cameraInputRef = useRef<HTMLInputElement>(null);
  const [form, setForm] = useState({
    username: user?.username || "",
    email: user?.email || "",
    phone: user?.phone || "",
    address: user?.address || "",
    avatar_url: user?.avatar_url || "",
    frequent_journeys: user?.frequent_journeys?.join(", ") || "",
  });
  const [saved, setSaved] = useState(false);

  useEffect(() => {
    djangoApi.get("/auth/profile").then(({ data }) => {
      setForm({
        username: data.username || "",
        email: data.email || "",
        phone: data.phone || "",
        address: data.address || "",
        avatar_url: data.avatar_url || "",
        frequent_journeys: (data.frequent_journeys || []).join(", "),
      });
    });
  }, []);

  async function save() {
    await djangoApi.put("/auth/profile", {
      ...form,
      frequent_journeys: form.frequent_journeys.split(",").map((item) => item.trim()).filter(Boolean),
    });
    await refreshUser();
    setSaved(true);
    window.setTimeout(() => setSaved(false), 1800);
  }

  function usePhoto(event: ChangeEvent<HTMLInputElement>) {
    const file = event.target.files?.[0];
    if (!file) return;

    const reader = new FileReader();
    reader.onload = () => {
      setForm((current) => ({ ...current, avatar_url: String(reader.result || "") }));
    };
    reader.readAsDataURL(file);
  }

  return (
    <section className="profile-page">
      <div className="profile-hero">
        <div className="profile-avatar">{form.avatar_url ? <img src={form.avatar_url} alt="" /> : form.username.slice(0, 1).toUpperCase()}</div>
        <div>
          <span>{admin ? "Admin Profile" : "Passenger Profile"}</span>
          <h1>{form.username || "Profile"}</h1>
          <p>{form.email}</p>
        </div>
      </div>
      <div className="photo-actions">
        <input ref={galleryInputRef} type="file" accept="image/*" onChange={usePhoto} />
        <input ref={cameraInputRef} type="file" accept="image/*" capture="user" onChange={usePhoto} />
        <button type="button" onClick={() => galleryInputRef.current?.click()}>Choose Photo</button>
        <button type="button" onClick={() => cameraInputRef.current?.click()}>Take Photo</button>
        {form.avatar_url && <button type="button" onClick={() => setForm({ ...form, avatar_url: "" })}>Remove Photo</button>}
      </div>
      <div className="profile-editor">
        <label>Username<input value={form.username} onChange={(e) => setForm({ ...form, username: e.target.value })} /></label>
        <label>Email<input type="email" value={form.email} onChange={(e) => setForm({ ...form, email: e.target.value })} /></label>
        <label>Phone<input value={form.phone} onChange={(e) => setForm({ ...form, phone: e.target.value })} /></label>
        <label>Address<textarea value={form.address} onChange={(e) => setForm({ ...form, address: e.target.value })} /></label>
        <label>Frequent Journeys<textarea value={form.frequent_journeys} onChange={(e) => setForm({ ...form, frequent_journeys: e.target.value })} /></label>
      </div>
      <button className="primary-action" onClick={save}>Save Profile</button>
      {saved && <p className="success">Profile updated.</p>}
    </section>
  );
}

export function PnrStatusPage() {
  const [bookings, setBookings] = useState<any[]>([]);
  useEffect(() => { djangoApi.get("/bookings/").then(({ data }) => setBookings(data.results || data)); }, []);
  return <PassengerModule title="PNR Status" rows={bookings.map((b) => [`PNR ${b.pnr}`, `${b.train_number} · ${b.journey_date}`, b.booking_status])} empty="No PNR records yet." />;
}

export function SavedJourneysPage() {
  const { user } = useAuth();
  const rows = (user?.frequent_journeys || ["NDLS-MMCT", "SBC-NDLS", "HWH-GHY"]).map((journey) => [journey, "Ready for quick search", "Saved"]);
  return <PassengerModule title="Saved Journeys" rows={rows} empty="No saved journeys yet." />;
}

export function WalletPage() {
  const [bookings, setBookings] = useState<any[]>([]);
  useEffect(() => { djangoApi.get("/bookings/").then(({ data }) => setBookings(data.results || data)); }, []);
  return <PassengerModule title="Payments" rows={bookings.map((b) => [b.pnr, currency(b.total_fare), b.payment_status || "Pending"])} empty="No payments yet." />;
}

export function NotificationsPage() {
  return <PassengerModule title="Alerts" rows={[["Carry ID proof", "Required for all passengers", "Active"], ["Journey calendar", "Past dates are blocked during search", "Enabled"], ["Refund status", "Refunds update after cancellation", "Ready"]]} empty="No alerts." />;
}

export function SupportPage() {
  return <PassengerModule title="Support" rows={[["Booking help", "Use My Bookings for tickets and cancellation", "Open"], ["Payment help", "Simulated payments are tracked in Payments", "Open"], ["Admin contact", "Use GRIDRAIL support counter for service changes", "Open"]]} empty="No support options." />;
}

function PassengerModule({ title, rows, empty }: { title: string; rows: string[][]; empty: string }) {
  return (
    <section className="page-card">
      <div className="section-title"><h1>{title}</h1><span>{rows.length} items</span></div>
      {rows.length === 0 ? <p className="empty">{empty}</p> : (
        <div className="module-list">
          {rows.map(([primary, secondary, status]) => (
            <article key={`${primary}-${secondary}`}>
              <div><strong>{primary}</strong><span>{secondary}</span></div>
              <small>{status}</small>
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

export function AdminDashboard() {
  const [stats, setStats] = useState<any>();
  const [reports, setReports] = useState<any>();
  useEffect(() => {
    djangoApi.get("/admin/dashboard").then(({ data }) => setStats(data));
    djangoApi.get("/admin/reports").then(({ data }) => setReports(data));
  }, []);
  const cards = stats ? [
    ["Total Users", stats.total_users],
    ["Total Trains", stats.total_trains],
    ["Total Stations", stats.total_stations],
    ["Today's Bookings", stats.todays_bookings],
    ["Confirmed Tickets", stats.confirmed_tickets],
    ["Cancelled Tickets", stats.cancelled_tickets],
    ["Revenue", currency(stats.revenue)],
    ["Pending Refunds", stats.pending_refunds]
  ] : [];
  return (
    <section className="dashboard">
      <h1>Admin Dashboard</h1>
      <div className="stat-grid">{cards.map(([label, value]) => <article key={label}><span>{label}</span><strong>{value}</strong></article>)}</div>
      <div className="chart-grid">
        <article><h2>Daily Bookings</h2><ResponsiveContainer height={240}><BarChart data={reports?.daily_bookings || []}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="day" /><YAxis /><Tooltip /><Bar dataKey="count" fill="#0f766e" /></BarChart></ResponsiveContainer></article>
        <article><h2>Occupancy</h2><OccupancyChart /></article>
      </div>
    </section>
  );
}

function OccupancyChart() {
  const [rows, setRows] = useState<any[]>([]);
  useEffect(() => { fastApi.get("/analytics/occupancy").then(({ data }) => setRows(data)); }, []);
  return <ResponsiveContainer height={240}><LineChart data={rows}><CartesianGrid strokeDasharray="3 3" /><XAxis dataKey="train_number" /><YAxis /><Tooltip /><Line dataKey="bookings" stroke="#b45309" strokeWidth={2} /></LineChart></ResponsiveContainer>;
}

export function ManagementPage({ title, endpoint }: { title: string; endpoint: string }) {
  const [rows, setRows] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);
  useEffect(() => {
    djangoApi.get(endpoint).then(({ data }) => setRows(data.results || data)).finally(() => setLoading(false));
  }, [endpoint]);
  const columns = rows[0] ? Object.keys(rows[0]).filter((key) => !Array.isArray(rows[0][key]) && typeof rows[0][key] !== "object").slice(0, 7) : [];
  return (
    <section className="page-card">
      <div className="section-title"><h1>{title}</h1><input placeholder="Search" /></div>
      {loading && <p>Loading...</p>}
      {!loading && rows.length === 0 && <p className="empty">No records found.</p>}
      {rows.length > 0 && <table><thead><tr>{columns.map((column) => <th key={column}>{column}</th>)}</tr></thead><tbody>{rows.map((row) => <tr key={row.id}>{columns.map((column) => <td key={column}>{String(row[column] ?? "")}</td>)}</tr>)}</tbody></table>}
    </section>
  );
}

export function ReportsPage() {
  const [reports, setReports] = useState<any>();
  useEffect(() => { djangoApi.get("/admin/reports").then(({ data }) => setReports(data)); }, []);
  return <section className="page-card"><h1>Reports & Analytics</h1><pre>{JSON.stringify(reports, null, 2)}</pre></section>;
}

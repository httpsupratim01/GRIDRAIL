import { ArrowRightLeft, CalendarDays, MapPin, Search, Train, Users } from "lucide-react";
import { FormEvent, useMemo, useState } from "react";
import { useNavigate } from "react-router-dom";
import { classes, todayPlus, todayPlusYears } from "../utils/format";

export type SearchState = {
  source: string;
  destination: string;
  journey_date: string;
  class_type: string;
  passengers: number;
};

export default function SearchWidget({ compact = false, title = "Find available trains", landing = false }: { compact?: boolean; title?: string; landing?: boolean }) {
  const navigate = useNavigate();
  const minDate = useMemo(() => todayPlus(1), []);
  const maxDate = useMemo(() => todayPlusYears(1), []);
  const popularRoutes = [
    ["NDLS", "MMCT"],
    ["SBC", "NDLS"],
    ["MAS", "HWH"],
    ["HYB", "NDLS"],
  ];
  const [form, setForm] = useState<SearchState>({
    source: "NDLS",
    destination: "MMCT",
    journey_date: todayPlus(7),
    class_type: "Sleeper",
    passengers: 1
  });

  function submit(event: FormEvent) {
    event.preventDefault();
    if (form.source === form.destination) return;
    if (form.journey_date < minDate) {
      setForm((current) => ({ ...current, journey_date: minDate }));
      return;
    }
    if (form.journey_date > maxDate) {
      setForm((current) => ({ ...current, journey_date: maxDate }));
      return;
    }
    const params = new URLSearchParams({
      ...form,
      passengers: String(form.passengers)
    });
    navigate(`/trains/results?${params.toString()}`);
  }

  function setPassengerCount(value: number) {
    setForm({ ...form, passengers: Math.min(20, Math.max(1, value || 1)) });
  }

  return (
    <form className={`search-widget search-panel ${compact ? "compact" : ""} ${landing ? "landing-search" : ""}`} onSubmit={submit}>
      <div className="search-heading">
        <div>
          <span><Train size={16} /> GRIDRAIL Search</span>
          <h2>{title}</h2>
        </div>
        <strong>{form.source} to {form.destination}</strong>
      </div>

      <div className="route-picker">
        <label>
          From
          <div className="input-icon">
            <MapPin size={17} />
            <input value={form.source} onChange={(e) => setForm({ ...form, source: e.target.value.toUpperCase() })} placeholder="NDLS" />
          </div>
        </label>
        <button className="swap-route" type="button" onClick={() => setForm({ ...form, source: form.destination, destination: form.source })} aria-label="Swap source and destination">
          <ArrowRightLeft size={18} />
        </button>
        <label>
          To
          <div className="input-icon">
            <MapPin size={17} />
            <input value={form.destination} onChange={(e) => setForm({ ...form, destination: e.target.value.toUpperCase() })} placeholder="MMCT" />
          </div>
        </label>
      </div>

      {!landing && (
        <div className="quick-routes">
          {popularRoutes.map(([source, destination]) => (
            <button type="button" key={`${source}-${destination}`} onClick={() => setForm({ ...form, source, destination })}>
              {source} to {destination}
            </button>
          ))}
        </div>
      )}

      <div className="journey-grid">
        <label>
          Journey Date
          <div className="date-field">
            <CalendarDays size={17} />
            <input type="date" min={minDate} max={maxDate} value={form.journey_date} onChange={(e) => setForm({ ...form, journey_date: e.target.value })} />
          </div>
          <small>Select any date within one year.</small>
        </label>
        <label>
          Passengers
          <div className="stepper-field">
            <Users size={17} />
            <button type="button" onClick={() => setPassengerCount(form.passengers - 1)}>-</button>
            <input type="number" min={1} max={20} value={form.passengers} onChange={(e) => setPassengerCount(Number(e.target.value))} />
            <button type="button" onClick={() => setPassengerCount(form.passengers + 1)}>+</button>
          </div>
          <small>You can enter 1 to 20 passengers.</small>
        </label>
      </div>

      <div className="class-picker" role="group" aria-label="Travel class">
        {classes.map((item) => (
          <button type="button" className={form.class_type === item ? "selected" : ""} key={item} onClick={() => setForm({ ...form, class_type: item })}>
            {item}
          </button>
        ))}
      </div>

      {form.source === form.destination && <p className="inline-error">Choose different stations.</p>}
      <button className="primary-action search-submit" type="submit">
        <Search size={18} />
        Search Trains
      </button>
    </form>
  );
}

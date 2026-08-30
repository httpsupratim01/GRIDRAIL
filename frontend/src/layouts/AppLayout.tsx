import { Bell, CalendarDays, CircleHelp, CreditCard, Heart, LayoutDashboard, LogOut, LucideIcon, Menu, Search, ShieldCheck, Ticket, Train, UserRound } from "lucide-react";
import { NavLink, Outlet } from "react-router-dom";
import { useAuth } from "../context/AuthContext";

export default function AppLayout() {
  const { user, logout } = useAuth();
  const passengerLinks: [string, string, LucideIcon][] = [
    ["/dashboard", "Dashboard", LayoutDashboard],
    ["/profile", "My Profile", UserRound],
    ["/trains/search", "Search Trains", Search],
    ["/bookings", "My Bookings", Ticket],
    ["/pnr-status", "PNR Status", ShieldCheck],
    ["/saved-journeys", "Saved Journeys", Heart],
    ["/wallet", "Payments", CreditCard],
    ["/notifications", "Alerts", Bell],
    ["/refunds", "Refund Status", Ticket],
    ["/support", "Support", CircleHelp],
    ["/change-password", "Change Password", ShieldCheck]
  ];
  const adminLinks: [string, string, LucideIcon][] = [
    ["/admin", "Admin Dashboard", LayoutDashboard],
    ["/admin/users", "Users", UserRound],
    ["/admin/trains", "Trains", Train],
    ["/admin/stations", "Stations", LayoutDashboard],
    ["/admin/routes", "Routes", Search],
    ["/admin/schedules", "Schedules", CalendarDays],
    ["/admin/coaches", "Coaches", Train],
    ["/admin/seats", "Seats", Ticket],
    ["/admin/fares", "Fares", CreditCard],
    ["/admin/bookings", "Bookings", Ticket],
    ["/admin/cancellations", "Cancellations", ShieldCheck],
    ["/admin/refunds", "Refunds", CreditCard],
    ["/admin/reports", "Reports", LayoutDashboard],
    ["/admin/profile", "Admin Profile", UserRound]
  ];
  const links = user?.role === "ADMIN" ? adminLinks : passengerLinks;

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <NavLink to="/" className="brand">
          <Train size={28} />
          GRIDRAIL
        </NavLink>
        {user && (
          <div className="sidebar-profile">
            {user.avatar_url ? <img src={user.avatar_url} alt="" /> : <span>{user.username.slice(0, 1).toUpperCase()}</span>}
            <div>
              <strong>{user.username}</strong>
              <small>{user.role}</small>
            </div>
          </div>
        )}
        <nav>
          {links.map(([to, label, Icon]) => (
            <NavLink key={to} to={to}>
              <Icon size={17} />
              {label}
            </NavLink>
          ))}
        </nav>
      </aside>
      <main className="main-panel">
        <header className="topbar">
          <div>
            <Menu size={20} />
            <span>{user ? `${user.username} · ${user.role}` : "Guest"}</span>
          </div>
          <div className="topbar-actions">
            {user?.role !== "ADMIN" && (
              <NavLink to="/trains/search">
                <CalendarDays size={18} />
                Plan Journey
              </NavLink>
            )}
            {user ? (
              <button onClick={logout}>
                <LogOut size={18} />
                Logout
              </button>
            ) : (
              <NavLink to="/login">
                <LayoutDashboard size={18} />
                Login
              </NavLink>
            )}
          </div>
        </header>
        <Outlet />
      </main>
    </div>
  );
}

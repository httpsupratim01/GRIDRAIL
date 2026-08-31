import { Navigate, Route, Routes } from "react-router-dom";
import AppLayout from "./layouts/AppLayout";
import { ChangePasswordPage, ForgotPasswordPage, LoginPage, RegisterPage, SimplePage } from "./pages/AuthPages";
import { AdminDashboard, ManagementPage, NotificationsPage, PassengerDashboard, PnrStatusPage, ProfilePage, ReportsPage, SavedJourneysPage, SupportPage, WalletPage } from "./pages/DashboardPages";
import Home from "./pages/Home";
import { BookingReviewPage, CancellationPage, CancelledTicketsPage, ConfirmationPage, MyBookingsPage, PassengerDetailsPage, PaymentPage, RefundStatusPage, SeatAvailabilityPage, TicketDetailsPage, TrainDetailsPage, TrainResultsPage, TrainSearchPage } from "./pages/TrainPages";

export default function App() {
  return (
    <Routes>
      <Route element={<AppLayout />}>
        <Route path="/" element={<Home />} />
        <Route path="/about" element={<SimplePage title="About Railway Reservation" body="A full-stack reservation portal with Django, FastAPI, PostgreSQL, and React." />} />
        <Route path="/contact" element={<SimplePage title="Contact" body="Support counters, helpline routing, and service messages can be managed by admins." />} />
        <Route path="/login" element={<LoginPage />} />
        <Route path="/admin/login" element={<LoginPage admin />} />
        <Route path="/register" element={<RegisterPage />} />
        <Route path="/forgot-password" element={<ForgotPasswordPage />} />
        <Route path="/dashboard" element={<PassengerDashboard />} />
        <Route path="/profile" element={<ProfilePage />} />
        <Route path="/trains/search" element={<TrainSearchPage />} />
        <Route path="/trains/results" element={<TrainResultsPage />} />
        <Route path="/trains/:id" element={<TrainDetailsPage />} />
        <Route path="/availability/:id" element={<SeatAvailabilityPage />} />
        <Route path="/passenger-details/:id" element={<PassengerDetailsPage />} />
        <Route path="/review/:id" element={<BookingReviewPage />} />
        <Route path="/payment/:id" element={<PaymentPage />} />
        <Route path="/confirmation/:id" element={<ConfirmationPage />} />
        <Route path="/bookings" element={<MyBookingsPage />} />
        <Route path="/pnr-status" element={<PnrStatusPage />} />
        <Route path="/saved-journeys" element={<SavedJourneysPage />} />
        <Route path="/wallet" element={<WalletPage />} />
        <Route path="/notifications" element={<NotificationsPage />} />
        <Route path="/support" element={<SupportPage />} />
        <Route path="/tickets/:id" element={<TicketDetailsPage />} />
        <Route path="/cancel/:id" element={<CancellationPage />} />
        <Route path="/cancellations" element={<CancelledTicketsPage />} />
        <Route path="/refunds" element={<RefundStatusPage />} />
        <Route path="/change-password" element={<ChangePasswordPage />} />
        <Route path="/admin" element={<AdminDashboard />} />
        <Route path="/admin/users" element={<ManagementPage title="User Management" endpoint="/users/" />} />
        <Route path="/admin/trains" element={<ManagementPage title="Train Management" endpoint="/trains/" />} />
        <Route path="/admin/stations" element={<ManagementPage title="Station Management" endpoint="/stations/" />} />
        <Route path="/admin/routes" element={<ManagementPage title="Route Management" endpoint="/routes/" />} />
        <Route path="/admin/schedules" element={<ManagementPage title="Schedule Management" endpoint="/routes/" />} />
        <Route path="/admin/coaches" element={<ManagementPage title="Coach Management" endpoint="/coaches/" />} />
        <Route path="/admin/seats" element={<ManagementPage title="Seat Management" endpoint="/seats/" />} />
        <Route path="/admin/fares" element={<ManagementPage title="Fare Management" endpoint="/fares/" />} />
        <Route path="/admin/bookings" element={<ManagementPage title="Booking Management" endpoint="/bookings/" />} />
        <Route path="/admin/cancellations" element={<ManagementPage title="Cancellation Management" endpoint="/cancellations/" />} />
        <Route path="/admin/refunds" element={<ManagementPage title="Refund Management" endpoint="/refunds/" />} />
        <Route path="/admin/reports" element={<ReportsPage />} />
        <Route path="/admin/profile" element={<ProfilePage admin />} />
        <Route path="*" element={<Navigate to="/" replace />} />
      </Route>
    </Routes>
  );
}

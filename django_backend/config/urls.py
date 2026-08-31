from django.contrib import admin
from django.urls import include, path
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenRefreshView

from accounts.views import ChangePasswordView, LoginView, ProfileView, RegisterView, UserViewSet
from bookings.views import BookingViewSet
from cancellations.views import CancellationViewSet, RefundViewSet
from payments.views import PaymentViewSet
from reports.views import DashboardStatsView, ReportsView
from stations.views import StationViewSet
from trains.views import CoachViewSet, FareViewSet, RouteViewSet, SeatViewSet, TrainViewSet

router = DefaultRouter()
router.register("users", UserViewSet, basename="users")
router.register("stations", StationViewSet, basename="stations")
router.register("trains", TrainViewSet, basename="trains")
router.register("routes", RouteViewSet, basename="routes")
router.register("coaches", CoachViewSet, basename="coaches")
router.register("seats", SeatViewSet, basename="seats")
router.register("fares", FareViewSet, basename="fares")
router.register("bookings", BookingViewSet, basename="bookings")
router.register("payments", PaymentViewSet, basename="payments")
router.register("cancellations", CancellationViewSet, basename="cancellations")
router.register("refunds", RefundViewSet, basename="refunds")

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/", include(router.urls)),
    path("api/auth/register", RegisterView.as_view(), name="register"),
    path("api/auth/login", LoginView.as_view(), name="login"),
    path("api/auth/refresh", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/auth/profile", ProfileView.as_view(), name="profile"),
    path("api/auth/change-password", ChangePasswordView.as_view(), name="change_password"),
    path("api/admin/dashboard", DashboardStatsView.as_view(), name="admin_dashboard"),
    path("api/admin/reports", ReportsView.as_view(), name="admin_reports"),
]

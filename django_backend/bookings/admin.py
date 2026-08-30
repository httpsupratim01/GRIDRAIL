from django.contrib import admin

from .models import Booking, Passenger, SeatReservation


class PassengerInline(admin.TabularInline):
    model = Passenger
    extra = 0


class SeatReservationInline(admin.TabularInline):
    model = SeatReservation
    extra = 0


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ("pnr", "user", "train", "journey_date", "class_type", "booking_status", "total_fare")
    search_fields = ("pnr", "user__email", "train__train_number")
    list_filter = ("booking_status", "class_type", "journey_date")
    inlines = [PassengerInline, SeatReservationInline]

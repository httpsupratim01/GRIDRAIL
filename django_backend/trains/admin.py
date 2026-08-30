from django.contrib import admin

from .models import Coach, Fare, Route, Seat, Train


class RouteInline(admin.TabularInline):
    model = Route
    extra = 0


class CoachInline(admin.TabularInline):
    model = Coach
    extra = 0


@admin.register(Train)
class TrainAdmin(admin.ModelAdmin):
    list_display = ("train_number", "train_name", "train_type", "source_station", "destination_station", "status")
    search_fields = ("train_number", "train_name")
    list_filter = ("train_type", "status")
    inlines = [RouteInline, CoachInline]


@admin.register(Route)
class RouteAdmin(admin.ModelAdmin):
    list_display = ("train", "sequence", "station", "arrival_time", "departure_time", "distance_from_source")


@admin.register(Coach)
class CoachAdmin(admin.ModelAdmin):
    list_display = ("train", "coach_number", "coach_type", "class_type", "total_seats", "status")


@admin.register(Seat)
class SeatAdmin(admin.ModelAdmin):
    list_display = ("coach", "seat_number", "seat_type", "status")


@admin.register(Fare)
class FareAdmin(admin.ModelAdmin):
    list_display = ("train", "class_type", "base_fare", "reservation_charge", "service_charge")

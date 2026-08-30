from django.contrib import admin

from .models import Station


@admin.register(Station)
class StationAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "city", "state", "zone", "status")
    search_fields = ("code", "name", "city")
    list_filter = ("zone", "status")

from django.contrib import admin

from .models import Cancellation, Refund


@admin.register(Cancellation)
class CancellationAdmin(admin.ModelAdmin):
    list_display = ("booking", "refund_amount", "cancellation_status", "cancellation_date")


@admin.register(Refund)
class RefundAdmin(admin.ModelAdmin):
    list_display = ("booking", "payment", "refund_amount", "refund_status", "refund_date")

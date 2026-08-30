from django.contrib import admin

from .models import Payment


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ("transaction_id", "booking", "payment_method", "amount", "payment_status", "payment_date")
    search_fields = ("transaction_id", "booking__pnr")
    list_filter = ("payment_method", "payment_status")

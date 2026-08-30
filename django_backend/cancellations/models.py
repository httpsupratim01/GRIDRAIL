from django.db import models


class Cancellation(models.Model):
    class Status(models.TextChoices):
        REQUESTED = "REQUESTED", "Requested"
        APPROVED = "APPROVED", "Approved"
        REJECTED = "REJECTED", "Rejected"

    booking = models.OneToOneField("bookings.Booking", on_delete=models.CASCADE, related_name="cancellation")
    cancellation_date = models.DateTimeField(auto_now_add=True)
    cancellation_reason = models.TextField(blank=True)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    cancellation_status = models.CharField(max_length=20, choices=Status.choices, default=Status.APPROVED)

    def __str__(self):
        return f"Cancellation {self.booking.pnr}"


class Refund(models.Model):
    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        PROCESSED = "PROCESSED", "Processed"
        FAILED = "FAILED", "Failed"

    booking = models.OneToOneField("bookings.Booking", on_delete=models.CASCADE, related_name="refund")
    payment = models.ForeignKey("payments.Payment", on_delete=models.PROTECT, related_name="refunds")
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    refund_status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    refund_date = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Refund {self.booking.pnr}"

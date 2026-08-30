from django.db import models


class Payment(models.Model):
    class Method(models.TextChoices):
        UPI = "UPI", "UPI"
        CREDIT_CARD = "CREDIT_CARD", "Credit Card"
        DEBIT_CARD = "DEBIT_CARD", "Debit Card"
        NET_BANKING = "NET_BANKING", "Net Banking"

    class Status(models.TextChoices):
        PENDING = "PENDING", "Pending"
        SUCCESSFUL = "SUCCESSFUL", "Successful"
        FAILED = "FAILED", "Failed"
        REFUNDED = "REFUNDED", "Refunded"

    booking = models.OneToOneField("bookings.Booking", on_delete=models.CASCADE, related_name="payment")
    transaction_id = models.CharField(max_length=40, unique=True, db_index=True)
    payment_method = models.CharField(max_length=20, choices=Method.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, db_index=True)
    payment_date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.transaction_id

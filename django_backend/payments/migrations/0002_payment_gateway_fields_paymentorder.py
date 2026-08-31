import django.db.models.deletion
from django.conf import settings
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ("bookings", "0001_initial"),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ("payments", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="payment",
            name="gateway_order_id",
            field=models.CharField(blank=True, db_index=True, max_length=80),
        ),
        migrations.AddField(
            model_name="payment",
            name="gateway_payment_id",
            field=models.CharField(blank=True, db_index=True, max_length=80),
        ),
        migrations.AddField(
            model_name="payment",
            name="gateway_signature",
            field=models.CharField(blank=True, max_length=160),
        ),
        migrations.CreateModel(
            name="PaymentOrder",
            fields=[
                ("id", models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name="ID")),
                ("provider_order_id", models.CharField(db_index=True, max_length=80, unique=True)),
                ("amount", models.DecimalField(decimal_places=2, max_digits=10)),
                ("currency", models.CharField(default="INR", max_length=3)),
                ("booking_payload", models.JSONField()),
                ("status", models.CharField(choices=[("CREATED", "Created"), ("PAID", "Paid"), ("FAILED", "Failed")], db_index=True, default="CREATED", max_length=20)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("booking", models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name="payment_order", to="bookings.booking")),
                ("user", models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name="payment_orders", to=settings.AUTH_USER_MODEL)),
            ],
        ),
    ]

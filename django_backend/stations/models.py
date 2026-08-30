from django.db import models


class Station(models.Model):
    class Status(models.TextChoices):
        ACTIVE = "ACTIVE", "Active"
        INACTIVE = "INACTIVE", "Inactive"

    name = models.CharField(max_length=120)
    code = models.CharField(max_length=12, unique=True)
    city = models.CharField(max_length=80)
    state = models.CharField(max_length=80)
    zone = models.CharField(max_length=80)
    status = models.CharField(max_length=20, choices=Status.choices, default=Status.ACTIVE, db_index=True)

    class Meta:
        ordering = ["name"]
        indexes = [models.Index(fields=["code", "city"])]

    def __str__(self):
        return f"{self.name} ({self.code})"

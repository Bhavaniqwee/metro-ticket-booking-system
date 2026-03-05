from django.db import models
from django.contrib.auth.models import User

class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)

    # store station names directly (simple & stable)
    source_station = models.CharField(max_length=100)
    destination_station = models.CharField(max_length=100)

    total_passengers = models.PositiveIntegerField()   # ✔ matches API
    total_amount = models.PositiveIntegerField()       # ✔ matches API

    created_at = models.DateTimeField(auto_now_add=True)
    is_return = models.BooleanField(default=False)

    def __str__(self):
        return f"Booking #{self.id}"


class Ticket(models.Model):
    booking = models.ForeignKey(
        Booking,
        related_name="tickets",
        on_delete=models.CASCADE
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    qr_code = models.ImageField(upload_to="qr_codes/")
    status = models.CharField(
        max_length=10,
        choices=[("BOOKED", "Booked"), ("CANCELLED", "Cancelled")],
        default="BOOKED"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    journey_type = models.CharField(
    max_length=10,
    choices=[("ONWARD", "Onward"), ("RETURN", "Return")],
    default="ONWARD"
)

    def __str__(self):
        return f"Ticket #{self.id}"

from django.db import models
from django.conf import settings
from django.contrib.auth.models import User

STATUS_CHOICES = [
    ('P', 'Pending'),
    ('A', 'Approved'),
    ('D', 'Denied'),
]

DAYS_OF_WEEK = [
    ('mon', 'Monday'),
    ('tue', 'Tuesday'),
    ('wed', 'Wednesday'),
    ('thu', 'Thursday'),
    ('fri', 'Friday'),
    ('sat', 'Saturday'),
    ('sun', 'Sunday'),
]

class Shift(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_dropped = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)

    def __str__(self):
        if self.user:
            return f"{self.user.username} - {self.date} ({self.start_time} to {self.end_time})"
        return f"Unassigned - {self.date} ({self.start_time} to {self.end_time})"

class TimeOffRequest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    start_date = models.DateField()
    end_date = models.DateField()
    reason = models.TextField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES, default='P')

    def __str__(self):
        return f"{self.user.username} - {self.start_date} to {self.end_date}"

class ShiftPickupRequest(models.Model):
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    approved = models.BooleanField(default=False)
    reviewed = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.requested_by.username} wants to pick up {self.shift}"

class Availability(models.Model):
    # link back to whatever User model you’re using
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='availabilities'
    )
    # limit it to one of the seven weekdays
    day = models.CharField(
        max_length=9,
        choices=DAYS_OF_WEEK
    )
    is_available = models.BooleanField(default=False)
    # allow blank/null so you can leave off if not available
    start_time = models.TimeField(blank=True, null=True)
    end_time   = models.TimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} – {self.day}"

class DroppedShift(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    shift = models.ForeignKey(Shift, on_delete=models.CASCADE)
    reason = models.TextField(blank=True, null=True)
    dropped_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} dropped shift on {self.shift.date}"

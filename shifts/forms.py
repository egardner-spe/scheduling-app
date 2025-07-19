from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User

from .models import TimeOffRequest, ShiftPickupRequest, Availability, Shift

# ─── Time choices for availability slots ────────────────────────────────────
HOURS = range(0, 24)
MINS = (0, 30)
TIME_CHOICES = [
    (f"{h:02d}:{m:02d}",
     f"{(h % 12 or 12)}:{m:02d} {'AM' if h < 12 else 'PM'}")
    for h in HOURS for m in MINS
]


# ─── Registration Form ──────────────────────────────────────────────────────
class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


# ─── Time-Off Request Form ──────────────────────────────────────────────────
class TimeOffRequestForm(forms.ModelForm):
    class Meta:
        model = TimeOffRequest
        fields = ['start_date', 'end_date', 'reason']


# ─── Shift Pickup Request Form ──────────────────────────────────────────────
class ShiftPickupRequestForm(forms.ModelForm):
    class Meta:
        model = ShiftPickupRequest
        fields = ['shift']  # user/requester is set in the view


# ─── Availability Form ──────────────────────────────────────────────────────
class AvailabilityForm(forms.ModelForm):
    is_available = forms.BooleanField(
        required=False,
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'})
    )
    start_time = forms.ChoiceField(
        required=False,
        choices=TIME_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )
    end_time = forms.ChoiceField(
        required=False,
        choices=TIME_CHOICES,
        widget=forms.Select(attrs={'class': 'form-select'})
    )

    class Meta:
        model = Availability
        # note: no 'day' here!
        fields = ['is_available', 'start_time', 'end_time']

# ─── ShiftForm ──────────────────────────────────────────────────────
class ShiftForm(forms.ModelForm):
    class Meta:
        model = Shift
        fields = ["start_time", "end_time"]
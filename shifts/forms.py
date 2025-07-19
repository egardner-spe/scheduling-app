from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from .models import TimeOffRequest, ShiftPickupRequest, Availability
from .forms import TIME_CHOICES #


# Generate 30-minute slots from 00:00 to 23:30
HOURS = range(0, 24)
MINS = (0, 30)
TIME_CHOICES = [
    (f"{h:02d}:{m:02d}", f"{(h%12 or 12)}:{m:02d} {'AM' if h < 12 else 'PM'}")
    for h in HOURS for m in MINS
]

class RegisterForm(UserCreationForm):
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

class TimeOffRequestForm(forms.ModelForm):
    class Meta:
        model = TimeOffRequest
        fields = ['start_date', 'end_date', 'reason']

class ShiftPickupRequestForm(forms.ModelForm):
    class Meta:
        model = ShiftPickupRequest
        fields = ['shift']  # User is set in the view, not on the form

class AvailabilityForm(forms.ModelForm):
    # Override the default so they’re not required
    available  = forms.BooleanField(required=False)
    start_time = forms.ChoiceField(choices=TIME_CHOICES, required=False)
    end_time   = forms.ChoiceField(choices=TIME_CHOICES, required=False)

    class Meta:
        model  = Availability
        fields = ['day', 'available', 'start_time', 'end_time']
        widgets = {
            'day': forms.HiddenInput(),
            'available': forms.CheckboxInput(attrs={'class':'form-check-input'}),
            'start_time': forms.Select(attrs={'class':'form-select'}),
            'end_time':   forms.Select(attrs={'class':'form-select'}),
        }


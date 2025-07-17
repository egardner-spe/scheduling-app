from django import forms
from .models import TimeOffRequest

class TimeOffRequestForm(forms.ModelForm):
    class Meta:
        model = TimeOffRequest
        fields = ['start_date', 'end_date', 'reason']
        widgets = {
            'start_date': forms.DateInput(attrs={'type': 'date'}),
            'end_date': forms.DateInput(attrs={'type': 'date'}),
        }

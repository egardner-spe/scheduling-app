from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.forms import formset_factory
from django.utils import timezone
from django.http import JsonResponse

from .models import Shift, TimeOffRequest, ShiftPickupRequest, Availability
from .forms import (
    TimeOffRequestForm,
    RegisterForm,
    ShiftPickupRequestForm,
    AvailabilityForm
)

def is_manager(user):
    return user.is_staff


@login_required
def dashboard(request):
    # Employee’s upcoming shifts
    shifts = (
        Shift.objects
        .filter(user=request.user, date__gte=timezone.now())
        .order_by('date')
    )

    # Their time-off requests
    time_off = (
        TimeOffRequest.objects
        .filter(user=request.user)
        .order_by('-start_date')
    )

    # Their availability
    availabilities = (
        Availability.objects
        .filter(user=request.user)
        .order_by('day')
    )

    # Open shifts they can claim
    available_shifts = (
        Shift.objects
        .filter(is_dropped=True, user=None)
        .order_by('date')
    )

    return render(request, 'shifts/dashboard.html', {
        'shifts': shifts,
        'time_off': time_off,
        'availabilities': availabilities,
        'available_shifts': available_shifts,
    })


def register(request):
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('dashboard')
    else:
        form = RegisterForm()

    return render(request, 'registration/register.html', {'form': form})


@login_required
def api_shifts(request):
    """Return JSON events for FullCalendar."""
    data = []
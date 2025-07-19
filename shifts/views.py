from django.shortcuts       import render, redirect, get_object_or_404
from django.contrib.auth    import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils           import timezone
from django.http            import JsonResponse

from .models  import Shift, TimeOffRequest, Availability, ShiftPickupRequest
from .forms   import (
    TimeOffRequestForm,
    RegisterForm,
    AvailabilityForm
)

# ---- Helpers ----
def is_manager(user):
    return user.is_staff

# ---- Dashboard View ----
@login_required
def dashboard(request):
    shifts = (
        Shift.objects
        .filter(user=request.user, date__gte=timezone.now())
        .order_by('date')
    )
    time_off       = TimeOffRequest.objects.filter(user=request.user).order_by('-start_date')
    availabilities = Availability.objects.filter(user=request.user).order_by('day')
    open_shifts    = Shift.objects.filter(is_dropped=True, user=None).order_by('date')

    return render(request, 'shifts/dashboard.html', {
        'shifts': shifts,
        'time_off': time_off,
        'availabilities': availabilities,
        'available_shifts': open_shifts,
    })

# ---- Registration ----
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

# ---- API for calendar ----
@login_required
def api_shifts(request):
    data = []
    for s in Shift.objects.filter(user=request.user):
        data.append({
            'title': f"{s.start_time.strftime('%-I:%M')}–{s.end_time.strftime('%-I:%M')}",
            'start': f"{s.date.isoformat()}T{s.start_time}",
            'end':   f"{s.date.isoformat()}T{s.end_time}",
        })
    return JsonResponse(data, safe=False)

# ---- Time Off ----
@login_required
def request_time_off(request):
    if request.method == 'POST':
        form = TimeOffRequestForm(request.POST)
        if form.is_valid():
            tor = form.save(commit=False)
            tor.user = request.user
            tor.save()
            return redirect('dashboard')
    else:
        form = TimeOffRequestForm()
    return render(request, 'shifts/request_time_off.html', {'form': form})

@login_required
def time_off_list(request):
    return render(request, 'shifts/time_off_list.html', {
        'time_off': TimeOffRequest.objects.filter(user=request.user)
    })

# …etc for the rest of your views…

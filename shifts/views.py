from django.shortcuts import render, redirect, get_object_or_404
from datetime import datetime, timedelta
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required, user_passes_test
from django.http import JsonResponse
from django.forms import formset_factory
from django.utils import timezone

from .models import Shift, TimeOffRequest, ShiftPickupRequest, Availability
from .forms  import (
    TimeOffRequestForm,
    RegisterForm,
    ShiftPickupRequestForm,
    AvailabilityForm,
)

def is_manager(user):
    return user.is_staff

# -----------------------------
# Dashboard & Registration
# -----------------------------

@login_required
def dashboard(request):
    # Upcoming shifts for this user
    shifts = (
        Shift.objects
        .filter(user=request.user, date__gte=timezone.now())
        .order_by('date', 'start_time')
    )

    # Their time-off requests
    time_off = (
        TimeOffRequest.objects
        .filter(user=request.user)
        .order_by('-start_date')
    )

    # Their availability entries
    availabilities = (
        Availability.objects
        .filter(user=request.user)
        .order_by('day')
    )

    # Open (dropped) shifts
    available_shifts = (
        Shift.objects
        .filter(is_dropped=True, user=None)
        .order_by('date', 'start_time')
    )

    return render(request, 'shifts/dashboard.html', {
        'shifts':           shifts,
        'time_off':         time_off,
        'availabilities':   availabilities,
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


# -----------------------------
# JSON API for FullCalendar
# -----------------------------

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


# -----------------------------
# Time Off Views
# -----------------------------

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

@user_passes_test(is_manager)
def admin_time_off_list(request):
    all_requests = TimeOffRequest.objects.all().order_by('-start_date')
    return render(request, 'shifts/admin_time_off_list.html', {
        'requests': all_requests
    })

@user_passes_test(is_manager)
def approve_time_off(request, request_id):
    tor = get_object_or_404(TimeOffRequest, id=request_id)
    tor.status = 'A'
    tor.save()
    return redirect('admin_time_off_list')

@user_passes_test(is_manager)
def deny_time_off(request, request_id):
    tor = get_object_or_404(TimeOffRequest, id=request_id)
    tor.status = 'D'
    tor.save()
    return redirect('admin_time_off_list')

@login_required
@user_passes_test(is_manager)
def edit_shift(request, shift_id):
    shift = get_object_or_404(Shift, id=shift_id)
    if request.method == 'POST':
        # pull from the POST—these must match your form field names
        shift.start_time = request.POST['start_time']
        shift.end_time   = request.POST['end_time']
        shift.save()
        return redirect('view_shift_schedule')
    return render(request, 'shifts/edit_shift.html', {
        'shift': shift,
        'time_choices': TIME_CHOICES,
    })


# -----------------------------
# Shift Drop & Pickup
# -----------------------------

@login_required
def drop_shift(request, shift_id):
    shift = get_object_or_404(Shift, id=shift_id, user=request.user)
    shift.is_dropped = True
    shift.user = None
    shift.save()
    return redirect('dashboard')

@login_required
def view_available_shifts(request):
    return render(request, 'shifts/available_shifts.html', {
        'available_shifts': Shift.objects.filter(is_dropped=True, user=None)
    })



@login_required
@user_passes_test(is_manager)
def view_shift_schedule(request):
    # 1) read “start” from the query-string, else default to today
    start_str = request.GET.get('start')
    if start_str:
        try:
            start = datetime.strptime(start_str, "%Y-%m-%d").date()
        except ValueError:
            start = timezone.localdate()
    else:
        start = timezone.localdate()

    # 2) snap back to Monday of that week
    start = start - timedelta(days=start.weekday())
    end   = start + timedelta(days=6)

    # 3) build your 7-day list
    week_days = [start + timedelta(days=i) for i in range(7)]

    # 4) pull all the shifts in that window
    shifts = Shift.objects.filter(date__range=(start, end))

    # 5) key them by “userID–YYYY-MM-DD” so the template can quick-lookup
    shift_map = {
        f"{s.user_id}-{s.date.isoformat()}": s
        for s in shifts
    }

    # 6) who shows up on this grid (all non-staff users)
    partners = User.objects.filter(is_staff=False).order_by("username")

    # 7) for prev/next links
    prev_week = start - timedelta(days=7)
    next_week = start + timedelta(days=7)

    return render(request, "shifts/shift_schedule.html", {
        "week_days": week_days,
        "shift_map": shift_map,
        "partners": partners,
        "prev_week": prev_week,
        "next_week": next_week,
    })

@login_required
@user_passes_test(is_manager)
def assign_shift(request, user_id, day):
    """
    Display a tiny form (start/end time) and on POST, create a Shift for that user on that date.
    """
    target_user = get_object_or_404(User, pk=user_id)
    the_date = parse_date(day)        # e.g. "2025-07-14" → date(2025,7,14)

    if request.method == "POST":
        form = ShiftForm(request.POST)
        if form.is_valid():
            shift = form.save(commit=False)
            shift.user = target_user
            shift.date = the_date
            shift.save()
            return redirect("view_shift_schedule")
    else:
        form = ShiftForm()

    return render(request, "shifts/assign_shift.html", {
        "form": form,
        "date": the_date,
        "partner": target_user,
    })
@login_required
def request_pickup_shift(request, shift_id):
    shift = get_object_or_404(Shift, id=shift_id, is_dropped=True, user=None)
    if ShiftPickupRequest.objects.filter(shift=shift, requested_by=request.user).exists():
        return redirect('dashboard')

    if request.method == 'POST':
        ShiftPickupRequest.objects.create(shift=shift, requested_by=request.user)
        return redirect('dashboard')

    return render(request, 'shifts/request_pickup_form.html', {'shift': shift})

@user_passes_test(is_manager)
def approve_pickup_requests(request):
    pending = ShiftPickupRequest.objects.filter(approved=False)
    return render(request, 'shifts/approve_shifts_pickup.html', {
        'requests': pending
    })

@user_passes_test(is_manager)
def approve_single_pickup(request, request_id):
    pr = get_object_or_404(ShiftPickupRequest, id=request_id)
    shift = pr.shift
    shift.user = pr.requested_by
    shift.is_dropped = False
    shift.save()
    pr.approved = True
    pr.save()
    return redirect('approve_shifts_pickup')

@user_passes_test(is_manager)
def deny_pickup_request(request, request_id):
    pr = get_object_or_404(ShiftPickupRequest, id=request_id)
    pr.delete()
    return redirect('approve_shifts_pickup')


# -----------------------------
# Availability Formset (7 days)
# -----------------------------

AvailabilityFormSet = formset_factory(AvailabilityForm, extra=0)

@login_required
def set_availability(request):
    DAYS = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    formset = AvailabilityFormSet(
        request.POST or None,
        initial=[{'day': d} for d in DAYS]
    )

    if request.method == 'POST' and formset.is_valid():
        for form, day in zip(formset.forms, DAYS):
            avail = form.save(commit=False)
            avail.user = request.user
            avail.day  = day
            avail.save()
        return redirect('dashboard')

    return render(request, 'shifts/set_availability.html', {
        'formset': formset
    })





@user_passes_test(is_manager)
def view_all_availabilities(request):
    return render(request, 'shifts/view_availabilities.html', {
        'availabilities': Availability.objects.all().order_by('user', 'day')
    })


# -----------------------------
# Extra: Drop-Shift List
# -----------------------------

@login_required
def drop_shift_list(request):
    shifts = Shift.objects.filter(user=request.user, is_dropped=False)
    return render(request, 'shifts/drop_shift_page.html', {'shifts': shifts})

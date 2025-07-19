from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required, user_passes_test
from django.forms import modelformset_factory, formset_factory
from django.utils import timezone
from django.http import JsonResponse
from .models import Shift, TimeOffRequest, ShiftPickupRequest, Availability
from .forms import TimeOffRequestForm, RegisterForm, ShiftPickupRequestForm, AvailabilityForm
from django.contrib.auth.decorators import user_passes_test

def is_manager(user):
    return user.is_staff

@login_required
def dashboard(request):
    # Employee’s upcoming shifts
    shifts = Shift.objects.filter(user=request.user, date__gte=timezone.now()).order_by('date')
    # Their time-off requests
    time_off = TimeOffRequest.objects.filter(user=request.user).order_by('-start_date')
    # Their availability
    availabilities = Availability.objects.filter(user=request.user).order_by('day')
    # Shifts up for grabs
    available_shifts = Shift.objects.filter(is_dropped=True, user=None).order_by('date')

    return render(request, 'shifts/dashboard.html', {
        'shifts': shifts,
        'time_off': time_off,
        'availabilities': availabilities,
        'available_shifts': available_shifts,
    })


@user_passes_test(is_manager)
def view_shift_schedule(request):
    """Manager‑only view: list every user’s shifts in date order."""
    shifts = (
        Shift.objects
        .select_related("user")
        .order_by("date", "start_time", "user__username")
    )
    return render(request, "shifts/shift_schedule.html", {"shifts": shifts})

def is_manager(user):
    return user.is_staff

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
def dashboard(request):
    shifts = Shift.objects.filter(user=request.user)
    return render(request, 'shifts/dashboard.html', {'shifts': shifts})

@login_required
def api_shifts(request):
    # Build a list of your user’s shifts in FullCalendar’s event format
    data = []
    for s in Shift.objects.filter(user=request.user):
        data.append({
            'title': f"{s.start_time.strftime('%-I:%M')}–{s.end_time.strftime('%-I:%M')}",
            'start': s.date.isoformat() + f"T{s.start_time}",
            'end':   s.date.isoformat() + f"T{s.end_time}",
        })
    return JsonResponse(data, safe=False)

@login_required
def request_time_off(request):
    if request.method == 'POST':
        form = TimeOffRequestForm(request.POST)
        if form.is_valid():
            time_off = form.save(commit=False)
            time_off.user = request.user
            time_off.save()
            return redirect('dashboard')
    else:
        form = TimeOffRequestForm()
    return render(request, 'shifts/request_time_off.html', {'form': form})

@login_required
def time_off_list(request):
    requests = TimeOffRequest.objects.filter(user=request.user)
    return render(request, 'shifts/time_off_list.html', {'requests': requests})

@user_passes_test(is_manager)
def admin_time_off_list(request):
    requests = TimeOffRequest.objects.all()
    return render(request, 'shifts/admin_time_off_list.html', {'requests': requests})

@user_passes_test(is_manager)
def approve_time_off(request, request_id):
    request_obj = get_object_or_404(TimeOffRequest, id=request_id)
    request_obj.status = 'A'
    request_obj.save()
    return redirect('admin_time_off_list')

@user_passes_test(is_manager)
def deny_time_off(request, request_id):
    request_obj = get_object_or_404(TimeOffRequest, id=request_id)
    request_obj.status = 'D'
    request_obj.save()
    return redirect('admin_time_off_list')

@login_required
def drop_shift(request, shift_id):
    shift = get_object_or_404(Shift, id=shift_id, user=request.user)
    shift.is_dropped = True
    shift.user = None  # Unassign the shift
    shift.save()
    return redirect('dashboard')

@login_required
def view_available_shifts(request):
    available_shifts = Shift.objects.filter(is_dropped=True, user=None)
    return render(request, 'shifts/available_shifts.html', {'available_shifts': available_shifts})

@login_required
def request_pickup_shift(request, shift_id):
    shift = get_object_or_404(Shift, id=shift_id, is_dropped=True, user=None)

    # Prevent duplicate requests
    if ShiftPickupRequest.objects.filter(shift=shift, requested_by=request.user).exists():
        return redirect('available_shifts')

    if request.method == 'POST':
        ShiftPickupRequest.objects.create(shift=shift, requested_by=request.user)
        return redirect('dashboard')

    return render(request, 'shifts/request_pickup_form.html', {'shift': shift})

@user_passes_test(is_manager)
def approve_pickup_requests(request):
    pending_requests = ShiftPickupRequest.objects.filter(approved=False)
    return render(request, 'shifts/approve_shifts_pickup.html', {'requests': pending_requests})

@user_passes_test(is_manager)
def approve_single_pickup(request, request_id):
    pickup_request = get_object_or_404(ShiftPickupRequest, id=request_id)
    shift = pickup_request.shift
    shift.user = pickup_request.requested_by
    shift.is_dropped = False
    shift.save()

    pickup_request.approved = True
    pickup_request.save()

    return redirect('approve_pickup_requests')

@user_passes_test(is_manager)
def deny_pickup_request(request, request_id):
    pickup_request = get_object_or_404(ShiftPickupRequest, id=request_id)
    pickup_request.delete()
    return redirect('approve_pickup_requests')

@login_required
def view_my_schedule(request):
    shifts = Shift.objects.filter(user=request.user).order_by('date')
    return render(request, 'shifts/my_schedule.html', {'shifts': shifts})


AvailabilityFormSet = modelformset_factory(
    Availability,
    form=AvailabilityForm,
    extra=7,          # one blank form per weekday
    can_delete=False  # up to you
)

@login_required
def set_availability(request):
    # 1) Define the seven weekdays
    DAYS = ['Monday','Tuesday','Wednesday','Thursday','Friday','Saturday','Sunday']
    # 2) Build a plain formset factory (no model-queryset binding)
    AvailabilityFormSet = formset_factory(AvailabilityForm, extra=0)

    if request.method == 'POST':
        # Bind POST data to the same number of forms
        formset = AvailabilityFormSet(request.POST, initial=[{'day': d} for d in DAYS])
        if formset.is_valid():
            # Save each form, filling in user & day
            for form, day in zip(formset.forms, DAYS):
                avail = form.save(commit=False)
                avail.user = request.user
                avail.day  = day
                avail.save()
            return redirect('dashboard')
    else:
        # On GET: create seven forms, each with its `day` pre-set
        initial_data = [{'day': d} for d in DAYS]
        formset = AvailabilityFormSet(initial=initial_data)

    return render(request, 'shifts/set_availability.html', {
        'formset': formset
    })



@user_passes_test(is_manager)
def view_all_availabilities(request):
    all_availability = Availability.objects.all().order_by('user')
    return render(request, 'shifts/view_availabilities.html', {'availabilities': all_availability})

@login_required
def drop_shift_list(request):
    shifts = Shift.objects.filter(user=request.user, is_dropped=False)
    return render(request, 'shifts/drop_shift_page.html', {'shifts': shifts})

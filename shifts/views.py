from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, user_passes_test
from django.utils.timezone import now
from .models import TimeOffRequest, Shift, ShiftPool
from .forms import TimeOffRequestForm


@login_required
def request_time_off(request):
    form = TimeOffRequestForm(request.POST or None)
    if form.is_valid():
        time_off = form.save(commit=False)
        time_off.employee = request.user
        time_off.save()
        return redirect('time_off_list')
    return render(request, 'shifts/request_time_off.html', {'form': form})

@login_required
def time_off_list(request):
    requests = TimeOffRequest.objects.filter(employee=request.user)
    return render(request, 'shifts/time_off_list.html', {'requests': requests})

@user_passes_test(lambda u: u.is_staff)
def review_time_off(request, request_id, action):
    req = get_object_or_404(TimeOffRequest, id=request_id)
    if action == 'approve':
        req.status = 'APPROVED'
    elif action == 'deny':
        req.status = 'DENIED'
    req.reviewed_by = request.user
    req.reviewed_at = now()
    req.save()
    return redirect('admin_time_off_requests')

@user_passes_test(lambda u: u.is_staff)
def admin_time_off_requests(request):
    requests = TimeOffRequest.objects.all()
    return render(request, 'shifts/admin_time_off_list.html', {'requests': requests})

def home(request):
    return render(request, 'shifts/home.html')

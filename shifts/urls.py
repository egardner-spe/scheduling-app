# shifts/urls.py
from django.urls import path
from . import views  # your views module

urlpatterns = [
    # ─── Dashboard & Registration ─────────────────────────────────────
    path('', views.dashboard,             name='dashboard'),
    path('register/', views.register,     name='register'),
    path('api/shifts/', views.api_shifts, name='api_shifts'),

    # ─── Employee Time Off ────────────────────────────────────────────
    path('request-time-off/', views.request_time_off, name='request_time_off'),
    path('my-time-off/',      views.time_off_list,    name='time_off_list'),

    # ─── Employee Availability ────────────────────────────────────────
    path('set-availability/', views.set_availability, name='set_availability'),

    # ─── Employee Open/Drop Shifts ───────────────────────────────────
    path('available-shifts/',     views.view_available_shifts, name='available_shifts'),
    path('drop-shift/<int:shift_id>/', views.drop_shift,         name='drop_shift'),
    path('my-shifts/drop/',         views.drop_shift_list,       name='drop_shift_list'),

    # ─── Shift Pickup (employee → manager approval) ──────────────────
    path('request-pickup/<int:shift_id>/',                 views.request_pickup_shift, name='request_pickup'),
    path('approve-shifts-pickup/',                        views.approve_pickup_requests, name='approve_shifts_pickup'),
    path('approve-shifts-pickup/approve/<int:request_id>/', views.approve_single_pickup,   name='approve_single_pickup'),
    path('approve-shifts-pickup/deny/<int:request_id>/',    views.deny_pickup_request,     name='deny_pickup_request'),

    # ─── Manager Time Off Approval ─────────────────────────────────
    path('admin/time-off/',                   views.admin_time_off_list, name='admin_time_off_list'),
    path('admin/time-off/approve/<int:request_id>/', views.approve_time_off,    name='approve_time_off'),
    path('admin/time-off/deny/<int:request_id>/',    views.deny_time_off,       name='deny_time_off'),

    # ─── Manager Availability Overview ───────────────────────────────
    path('admin/view-availabilities/', views.view_all_availabilities, name='view_availabilities'),

    # ─── Manager Full Schedule Calendar ──────────────────────────────
    path('admin/schedule/',                       views.view_shift_schedule, name='view_shift_schedule'),
    path('admin/schedule/edit/<int:shift_id>/',   views.edit_shift,          name='edit_shift'),
    path('admin/schedule/assign/<int:user_id>/<str:day>/', views.assign_shift, name='assign_shift'),
]

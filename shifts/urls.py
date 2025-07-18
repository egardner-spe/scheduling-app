from django.urls import path
from . import views

urlpatterns = [
    # Authentication & Home
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),

    # Time Off Requests
    path('request-time-off/', views.request_time_off, name='request_time_off'),
    path('my-time-off/', views.time_off_list, name='time_off_list'),
    path('admin/time-off/', views.admin_time_off_list, name='admin_time_off_list'),
    path('admin/time-off/approve/<int:request_id>/', views.approve_time_off, name='approve_time_off'),
    path('admin/time-off/deny/<int:request_id>/', views.deny_time_off, name='deny_time_off'),

    # Shift Drop & Pickup
    path('drop-shift/<int:shift_id>/', views.drop_shift, name='drop_shift'),
    path('available-shifts/', views.view_available_shifts, name='available_shifts'),
    path('request-pickup/<int:shift_id>/', views.request_pickup_shift, name='request_pickup'),
    path('approve-shifts-pickup/', views.approve_pickup_requests, name='approve_shifts_pickup'),
    path('approve-shifts-pickup/approve/<int:request_id>/', views.approve_single_pickup, name='approve_single_pickup'),
    path('approve-shifts-pickup/deny/<int:request_id>/', views.deny_pickup_request, name='deny_pickup_request'),
    path('my-shifts/drop/', views.drop_shift_list, name='drop_shift_list'),

    # Manager - Full Shift Schedule View
    path('admin/schedule/', views.view_shift_schedule, name='view_shift_schedule'),

    # Schedule & Availability
    path('my-schedule/', views.view_my_schedule, name='user_schedule'),
    path('set-availability/', views.set_availability, name='set_availability'),

    # Optional: View all users’ availabilities (Manager only)
    path('admin/view-availabilities/', views.view_all_availabilities, name='view_availabilities'),
]

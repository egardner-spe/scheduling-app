from django.urls import path
from .            import views

urlpatterns = [
    path('',                          views.dashboard,              name='dashboard'),
    path('register/',                 views.register,               name='register'),
    path('api/shifts/',               views.api_shifts,             name='api_shifts'),

    # Time Off
    path('request-time-off/',         views.request_time_off,       name='request_time_off'),
    path('my-time-off/',              views.time_off_list,          name='time_off_list'),

    # Availability
    path('set-availability/',         views.set_availability,       name='set_availability'),

    # Open Shifts
    path('available-shifts/',         views.view_available_shifts,  name='available_shifts'),

    # Pickup
    path('request-pickup/<int:shift_id>/', views.request_pickup_shift,   name='request_pickup'),
    path('approve-shifts-pickup/',    views.approve_pickup_requests, name='approve_shifts_pickup'),
    path('approve-shifts-pickup/approve/<int:request_id>/',
         views.approve_single_pickup, name='approve_single_pickup'),
    path('approve-shifts-pickup/deny/<int:request_id>/',
         views.deny_pickup_request,   name='deny_pickup_request'),
]

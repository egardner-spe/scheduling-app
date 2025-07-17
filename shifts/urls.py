from django.urls import path
from . import views

urlpatterns = [
    path('request-time-off/', views.request_time_off, name='request_time_off'),
    path('my-time-off/', views.time_off_list, name='time_off_list'),
    path('admin/time-off/', views.admin_time_off_requests, name='admin_time_off_requests'),
    path('admin/time-off/<int:request_id>/<str:action>/', views.review_time_off, name='review_time_off'),
]

from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    # 1) All of your app’s URLs live in shifts/urls.py
    path('', include('shifts.urls')),

    # 2) Authentication (login/logout/password-reset)
    path('', include('django.contrib.auth.urls')),

    # 3) Django’s real admin site
    path('admin/', admin.site.urls),
]

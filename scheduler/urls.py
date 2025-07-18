from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shifts.urls')),  # Routes to your app-level URLs
    path('', include('django.contrib.auth.urls')),  # ✅ Enables login/logout/reset views
]

from django.contrib import admin
from .models import Shift, TimeOffRequest

@admin.register(Shift)
class ShiftAdmin(admin.ModelAdmin):
    list_display = ('user', 'date', 'start_time', 'end_time')

@admin.register(TimeOffRequest)
class TimeOffRequestAdmin(admin.ModelAdmin):
    list_display = ('user', 'start_date', 'end_date', 'reason', 'status')
    list_filter = ('status',)

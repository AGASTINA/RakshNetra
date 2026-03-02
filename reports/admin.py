from django.contrib import admin
from .models import EventReport

@admin.register(EventReport)
class EventReportAdmin(admin.ModelAdmin):
    list_display = ('event', 'generated_at', 'generated_by')
    readonly_fields = ('generated_at',)

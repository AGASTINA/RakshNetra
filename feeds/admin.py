from django.contrib import admin
from .models import CameraFeed, Alert

@admin.register(CameraFeed)
class CameraFeedAdmin(admin.ModelAdmin):
    list_display = ('name', 'protocol', 'enabled', 'mode')
    list_filter = ('protocol', 'enabled', 'mode')

@admin.register(Alert)
class AlertAdmin(admin.ModelAdmin):
    list_display = ('timestamp', 'threat_type', 'severity', 'confidence')
    readonly_fields = ('timestamp',)

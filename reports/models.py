from django.db import models
from django.conf import settings

class EventReport(models.Model):
    event = models.OneToOneField('events.Event', on_delete=models.CASCADE)
    generated_at = models.DateTimeField(auto_now_add=True)
    generated_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    
    summary = models.TextField(blank=True, help_text='AI-generated summary')
    detection_timeline = models.JSONField(default=dict, blank=True)
    threat_heatmap = models.ImageField(upload_to='reports/heatmaps/', null=True, blank=True)
    incident_breakdown = models.JSONField(default=dict, blank=True)
    suspect_paths = models.JSONField(default=dict, blank=True)
    response_times = models.JSONField(default=dict, blank=True)
    
    pdf_file = models.FileField(upload_to='reports/pdf/', null=True, blank=True)
    digital_report = models.FileField(upload_to='reports/digital/', null=True, blank=True)

    def __str__(self):
        return f"Report for {self.event.name}"

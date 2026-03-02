from django.db import models
from django.conf import settings

class Event(models.Model):
    THREAT_LOW = 'low'
    THREAT_MEDIUM = 'medium'
    THREAT_HIGH = 'high'

    THREAT_CHOICES = [
        (THREAT_LOW, 'Low'),
        (THREAT_MEDIUM, 'Medium'),
        (THREAT_HIGH, 'High'),
    ]

    name = models.CharField(max_length=200)
    start_time = models.DateTimeField()
    end_time = models.DateTimeField()
    location = models.CharField(max_length=255, blank=True)
    coordinates = models.CharField(max_length=100, blank=True)
    threat_level = models.CharField(max_length=20, choices=THREAT_CHOICES, default=THREAT_LOW)
    description = models.TextField(blank=True)
    vip_notes = models.TextField(blank=True)
    video_file = models.FileField(upload_to='event_videos/%Y/%m/%d/', null=True, blank=True)
    detection_report = models.JSONField(null=True, blank=True)
    created_by = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)

    def __str__(self):
        return f"{self.name} ({self.start_time.date()})"

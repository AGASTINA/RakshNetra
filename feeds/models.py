from django.db import models
from django.conf import settings

class CameraFeed(models.Model):
    PROTO_WEBCAM = 'webcam'
    PROTO_RTSP = 'rtsp'
    PROTO_RTMP = 'rtmp'
    PROTO_HTTP = 'http'
    PROTO_HLS = 'hls'
    PROTO_FILE = 'file'

    PROTOCOL_CHOICES = [
        (PROTO_WEBCAM, 'USB Webcam'),
        (PROTO_RTSP, 'RTSP (IP Camera/CCTV)'),
        (PROTO_RTMP, 'RTMP'),
        (PROTO_HTTP, 'HTTP/HTTPS'),
        (PROTO_HLS, 'HLS (m3u8)'),
        (PROTO_FILE, 'Video File'),
    ]

    MODE_PREVIEW = 'preview'
    MODE_AI = 'ai'
    MODE_CHOICES = [
        (MODE_PREVIEW, 'Preview Mode (Browser)'),
        (MODE_AI, 'AI Mode (OpenCV)'),
    ]

    name = models.CharField(max_length=200)
    protocol = models.CharField(max_length=20, choices=PROTOCOL_CHOICES)
    source = models.CharField(max_length=500, help_text='URL, file path, device index, etc.')
    mode = models.CharField(max_length=20, choices=MODE_CHOICES, default=MODE_PREVIEW)
    enabled = models.BooleanField(default=True)
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE, null=True, blank=True)
    
    # AI model assignment
    assigned_models = models.ManyToManyField('ai.AIModel', blank=True)

    def __str__(self):
        return f"{self.name} ({self.protocol})"

class Alert(models.Model):
    SEVERITY_INFO = 'info'
    SEVERITY_WARNING = 'warning'
    SEVERITY_CRITICAL = 'critical'

    SEVERITY_CHOICES = [
        (SEVERITY_INFO, 'INFO'),
        (SEVERITY_WARNING, 'WARNING'),
        (SEVERITY_CRITICAL, 'CRITICAL'),
    ]

    event = models.ForeignKey('events.Event', on_delete=models.CASCADE)
    camera = models.ForeignKey(CameraFeed, on_delete=models.SET_NULL, null=True)
    threat_type = models.CharField(max_length=100)
    severity = models.CharField(max_length=20, choices=SEVERITY_CHOICES, default=SEVERITY_WARNING)
    confidence = models.FloatField()
    timestamp = models.DateTimeField(auto_now_add=True)
    snapshot = models.ImageField(upload_to='alert_snapshots/', null=True, blank=True)
    location = models.CharField(max_length=255, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.threat_type} - {self.severity} ({self.timestamp.isoformat()})"

from django.db import models
from django.conf import settings
from django.utils import timezone

class MapLayout(models.Model):
    event = models.OneToOneField('events.Event', on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=200, default='Default Map')
    image = models.ImageField(upload_to='map_layouts/')
    width_pixels = models.IntegerField()
    height_pixels = models.IntegerField()
    width_meters = models.FloatField(help_text='Physical width in meters', default=1.0)
    height_meters = models.FloatField(help_text='Physical height in meters', default=1.0)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        if self.event:
            return f"Map for {self.event.name}"
        return self.name

class MapObject(models.Model):
    TYPE_WALL = 'wall'
    TYPE_DOOR = 'door'
    TYPE_CAMERA = 'camera'
    TYPE_CCTV = 'cctv'
    TYPE_UNIT = 'nsg_unit'
    TYPE_RESTRICTION = 'restricted_zone'
    TYPE_SUSPECT = 'suspect'
    TYPE_POLICE = 'police'
    TYPE_VIP = 'vip'
    TYPE_GATE = 'gate'
    TYPE_ENTRY = 'entry'
    TYPE_EXIT = 'exit'

    TYPE_CHOICES = [
        (TYPE_WALL, 'Wall'),
        (TYPE_DOOR, 'Door'),
        (TYPE_CAMERA, 'Camera'),
        (TYPE_CCTV, 'CCTV'),
        (TYPE_UNIT, 'NSG Unit'),
        (TYPE_RESTRICTION, 'Restricted Zone'),
        (TYPE_SUSPECT, 'Suspect'),
        (TYPE_POLICE, 'Police'),
        (TYPE_VIP, 'VIP'),
        (TYPE_GATE, 'Gate'),
        (TYPE_ENTRY, 'Entry'),
        (TYPE_EXIT, 'Exit'),
    ]

    map_layout = models.ForeignKey(MapLayout, on_delete=models.CASCADE)
    obj_type = models.CharField(max_length=50, choices=TYPE_CHOICES)
    x = models.FloatField()
    y = models.FloatField()
    label = models.CharField(max_length=100, blank=True)
    metadata = models.JSONField(default=dict, blank=True)

    def __str__(self):
        return f"{self.obj_type} - {self.label}"

class SuspectPosition(models.Model):
    event = models.ForeignKey('events.Event', on_delete=models.CASCADE)
    x = models.FloatField()
    y = models.FloatField()
    camera = models.ForeignKey('feeds.CameraFeed', on_delete=models.SET_NULL, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Suspect ({self.x:.2f}, {self.y:.2f}) at {self.timestamp.isoformat()}"

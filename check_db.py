#!/usr/bin/env python
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rakshnetra.settings')
django.setup()

from events.models import Event
from feeds.models import CameraFeed
from ai.models import AIModel

print("=== DATABASE STATUS ===")
print(f"Events: {Event.objects.count()}")
print(f"Cameras: {CameraFeed.objects.count()}")
print(f"AI Models (Active): {AIModel.objects.filter(is_active=True).count()}")
print(f"AI Models (Total): {AIModel.objects.count()}")

if Event.objects.exists():
    print("\nSample Events:")
    for e in Event.objects.all()[:3]:
        print(f"  - {e.name} (type: {e.event_type})")
else:
    print("\nNo events in database")

if CameraFeed.objects.exists():
    print("\nSample Cameras:")
    for c in CameraFeed.objects.all()[:3]:
        print(f"  - {c.name} (enabled: {c.enabled})")
else:
    print("\nNo cameras in database")

if AIModel.objects.exists():
    print("\nActive Models:")
    for m in AIModel.objects.filter(is_active=True):
        print(f"  - {m.name} (type: {m.model_type})")
else:
    print("\nNo models in database")

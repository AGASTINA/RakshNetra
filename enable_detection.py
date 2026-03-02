import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rakshnetra.settings')
django.setup()

from feeds.models import CameraFeed

cam = CameraFeed.objects.get(id=8)
print(f"Camera: {cam.name}")
print(f"  ID: {cam.id}")
print(f"  Protocol: {cam.protocol}")
print(f"  Source: {cam.source}")
print(f"  Mode: {cam.mode}")
print(f"  Enabled: {cam.enabled}")
print(f"  Status: {'READY' if cam.protocol == 'file' else 'WAITING FOR INPUT'}")

print("\n--- Changing mode to AI for face detection ---")
cam.mode = 'ai'
cam.save()
print(f"✓ Updated to MODE: {cam.mode}")
print("\n✓ Face detection will now run on the video stream!")

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rakshnetra.settings')
django.setup()

from feeds.models import CameraFeed

cam = CameraFeed.objects.get(id=8)

print(f"Camera: {cam.name}")
print(f"  Current enabled: {cam.enabled}")
print(f"  Current mode: {cam.mode}")

# Enable the camera
cam.enabled = True
cam.save()

print(f"\n✓ Camera enabled: {cam.enabled}")
print(f"✓ Camera mode: {cam.mode}")
print(f"\n✓ Ready for face detection!")

import os
import django
import shutil

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rakshnetra.settings')
django.setup()

from feeds.models import CameraFeed

# Check if source video exists
source_video = r"c:\Users\agast\Videos\fight.mp4"
if not os.path.exists(source_video):
    print(f"✗ Video not found: {source_video}")
    exit(1)

# Copy to media folder
media_path = "media/fight.mp4"
try:
    shutil.copy(source_video, media_path)
    size = os.path.getsize(media_path) / 1024 / 1024
    print(f"✓ Copied video to {media_path}")
    print(f"  Size: {size:.2f} MB")
except Exception as e:
    print(f"✗ Error copying: {e}")
    exit(1)

# Create new camera for fighting detection
try:
    # Check if it already exists
    cam = CameraFeed.objects.filter(name='fight').first()
    if cam:
        print(f"✓ Camera 'fight' already exists (ID: {cam.id})")
        cam.source = media_path
        cam.protocol = 'file'
        cam.mode = 'ai'
        cam.enabled = True
        cam.save()
        print(f"  Updated with video source")
    else:
        # Create new camera
        cam = CameraFeed.objects.create(
            name='fight',
            protocol='file',
            source=media_path,
            mode='ai',
            enabled=True
        )
        print(f"✓ Created camera 'fight' (ID: {cam.id})")
        print(f"  Protocol: file")
        print(f"  Mode: AI (detection enabled)")
        
except Exception as e:
    print(f"✗ Error creating camera: {e}")
    exit(1)

print("\n✓ Fighting detection video ready!")
print(f"\nCamera will detect:")
print(f"  👤 Face Recognition")
print(f"  ⚔️ Fighting Detection")
print(f"  🧑‍🤝‍🧑 Person Clustering")
print(f"  ⚠️ Suspicious Behavior")

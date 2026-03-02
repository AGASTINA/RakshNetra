import os
import sys
import django

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
sys.path.insert(0, BASE_DIR)

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rakshnetra.settings')
django.setup()

from django.conf import settings
from feeds.models import CameraFeed

videos_dir = os.path.join(settings.MEDIA_ROOT, 'videos')
os.makedirs(videos_dir, exist_ok=True)

dummy_path = os.path.join(videos_dir, 'dummy_test_file.mp4')
# Create a small dummy file (not a valid video) to test source handling
with open(dummy_path, 'wb') as f:
    f.write(b"this is a dummy test file for OpenCV path testing\n")

abs_path = dummy_path.replace('\\', '/')

camera = CameraFeed.objects.create(
    name='Test Dummy Camera',
    protocol=CameraFeed.PROTO_FILE,
    source=abs_path,
    mode=CameraFeed.MODE_PREVIEW,
    enabled=True,
)

print(f"Created camera id={camera.id} source={camera.source}")

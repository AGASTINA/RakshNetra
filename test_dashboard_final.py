import urllib.request
urlopen = urllib.request.urlopen

# Test that dashboard loads without errors
print("Testing dashboard endpoints...\n")

try:
    # Test that the HTML includes our data
    response = urlopen('http://127.0.0.1:8000/').read().decode('utf-8')
    if '<title>RakshNetra' in response and 'accounts/login' in response:
        print("✓ Login redirect works (not authenticated)")
    else:
        print("✗ Unexpected response")
except Exception as e:
    print(f"✗ Connection error: {e}")

# Quick check of serializer
import django, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rakshnetra.settings')
django.setup()

from feeds.serializers import CameraFeedSerializer
from feeds.models import CameraFeed

camera = CameraFeed.objects.first()
if camera:
    serializer = CameraFeedSerializer(camera)
    print(f"\n✓ CameraFeedSerializer works")
    print(f"  - Data keys: {list(serializer.data.keys())}")
    if 'detected_video_url' in serializer.data:
        print(f"  - detected_video_url field present: {serializer.data['detected_video_url']}")

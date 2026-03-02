import django, json, os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rakshnetra.settings')
django.setup()

from feeds.serializers import CameraFeedSerializer
from feeds.models import CameraFeed

cam = CameraFeed.objects.get(id=8)
serializer = CameraFeedSerializer(cam)
data = serializer.data

print('Camera 8 (president) - Serialized Data:')
print(f'  Name: {data["name"]}')
print(f'  Protocol: {data["protocol"]}')
print(f'  Source: {data["source"]}')
print(f'  Enabled: {data["enabled"]}')
print(f'  Detected Video URL: {data.get("detected_video_url", "None")}')
print()
print('✓ Ready for dashboard rendering with video controls')

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rakshnetra.settings')
django.setup()

from feeds.models import CameraFeed
from events.models import Event
from ai.models import AIModel
import json
from django.core.serializers.json import DjangoJSONEncoder

# Test the code that was failing
try:
    cameras = list(CameraFeed.objects.all().values('id', 'name', 'enabled', 'protocol', 'source'))
    events_queryset = Event.objects.all().order_by('-start_time')
    
    # Convert events to dict with explicit datetime formatting
    events = []
    for event in events_queryset:
        events.append({
            'id': event.id,
            'name': event.name,
            'location': event.location,
            'threat_level': event.threat_level,
            'start_time': event.start_time.isoformat() if event.start_time else ''
        })
    
    # Convert to JSON strings for template embedding using DjangoJSONEncoder 
    cameras_json = json.dumps(cameras, cls=DjangoJSONEncoder)
    events_json = json.dumps(events, cls=DjangoJSONEncoder)
    
    print("✓ Cameras JSON serialization successful")
    print(f"  Cameras count: {len(cameras)}")
    print(f"  Cameras JSON length: {len(cameras_json)}")
    
    print("✓ Events JSON serialization successful")
    print(f"  Events count: {len(events)}")
    print(f"  Events JSON length: {len(events_json)}")
    
    print("\n✓ All JSON serialization tests passed!")
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)

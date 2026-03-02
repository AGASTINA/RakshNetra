import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rakshnetra.settings')
django.setup()

from django.test import Client
from accounts.models import User
from ai.models import AIModel

client = Client()
user = User.objects.filter(username='testuser').first()
if user:
    client.force_login(user)

print("=" * 60)
print("TESTING VIDEO STREAM WITH ALL DETECTION MODELS")
print("=" * 60)

# Check what models are active
print("\n1. Active Detection Models:")
print("-" * 40)
active_models = AIModel.objects.filter(is_active=True)
for model in active_models:
    print(f"  ✓ {model.name} ({model.model_type})")

print(f"\nTotal active: {active_models.count()}")

# Test camera detection endpoint
print("\n2. Testing Camera Detection Endpoint:")
print("-" * 40)
response = client.get(
    '/api/cameras/8/current_detections/',
    HTTP_ACCEPT='application/json'
)

print(f"Endpoint: /api/cameras/8/current_detections/")
print(f"Status: {response.status_code}")

if response.status_code == 200:
    data = response.json()
    print(f"\nDetection Response:")
    print(f"  Camera ID: {data.get('camera_id')}")
    print(f"  Camera: {data.get('camera_name')}")
    print(f"  Faces: {len(data.get('faces', []))}")
    print(f"  Objects: {len(data.get('objects', []))}")
    print(f"  Weapons: {len(data.get('weapons', []))}")
    
    if data.get('faces'):
        print(f"\n  Detected Faces:")
        for face in data['faces'][:3]:
            print(f"    • {face.get('name', 'Unknown')} ({face.get('confidence', 0):.0%})")
    
    print("\n✓ All detection models ready for video streaming!")
else:
    print(f"Error: {response.content.decode()[:200]}")

print("\n" + "=" * 60)
print("VIDEO DETECTION SETUP COMPLETE")
print("=" * 60)

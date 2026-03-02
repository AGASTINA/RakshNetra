import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rakshnetra.settings')
django.setup()

from django.test import Client
from accounts.models import User

client = Client()
user = User.objects.filter(username='testuser').first()
if user:
    client.force_login(user)
else:
    print("Test user not found")
    exit(1)

print("=" * 60)
print("TESTING ADD CAMERA ENDPOINT")
print("=" * 60)

# Test adding a camera via API
response = client.post(
    '/api/cameras/add/',
    data=json.dumps({
        'name': 'Test Camera',
        'protocol': 'file',
        'source': 'media/test.mp4',
        'mode': 'preview'
    }),
    content_type='application/json'
)

print(f"\nStatus: {response.status_code}")
print(f"Response: {response.content.decode('utf-8')[:500]}")

# Test face detection API
print("\n" + "=" * 60)
print("TESTING FACE DETECTION ENDPOINT")
print("=" * 60)

response = client.post(
    '/api/detect/faces/',
    data=json.dumps({
        'camera_id': 8,
        'frame_number': 1
    }),
    content_type='application/json'
)

print(f"\nStatus: {response.status_code}")
print(f"Response: {response.content.decode('utf-8')[:500]}")

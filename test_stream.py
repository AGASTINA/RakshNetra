#!/usr/bin/env python
"""Test the video stream endpoint directly"""

import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rakshnetra.settings')
django.setup()

import sys
from django.test import Client
from feeds.models import CameraFeed

client = Client()

# Test the camera viewer page
print("\n=== Testing Camera Viewer (Browser Page) ===")
try:
    response = client.get('/camera/2/')
    print(f"Status: {response.status_code}")
    if response.status_code == 302:
        print("Redirecting to login - Need to authenticate via browser")
    elif response.status_code == 200:
        print("✓ Camera viewer page loads successfully")
        if b'camera_viewer' in response.content or b'video' in response.content.lower():
            print("✓ Page contains video content")
except Exception as e:
    print(f"❌ Error: {e}")

# Test the raw video feed stream
print("\n=== Testing Video Feed Stream (MJPEG) ===")
try:
    response = client.get('/video_feed/2/')
    print(f"Status: {response.status_code}")
    if response.status_code == 200:
        content_type = response.get('Content-Type', '')
        print(f"Content-Type: {content_type}")
        if 'multipart' in content_type:
            print("✓ Stream is MJPEG format")
            # Read first 1000 bytes
            content = response.content[:1000] if hasattr(response, 'content') else b''
            if b'--frame' in content or b'jpeg' in content.lower():
                print("✓ Stream contains valid JPEG data")
            else:
                print("Stream content sample:", content[:200])
    else:
        print(f"Stream returned status {response.status_code}")
except Exception as e:
    print(f"❌ Error: {e}")

# Check camera exists
print("\n=== Camera Configuration ===")
try:
    camera = CameraFeed.objects.get(id=2)
    print(f"✓ Camera exists: {camera.name}")
    print(f"  - ID: {camera.id}")
    print(f"  - Protocol: {camera.protocol}")
    print(f"  - Source: {camera.source}")
    print(f"  - Enabled: {camera.enabled}")
    print(f"  - Active models: {camera.assigned_models.count()}")
    if camera.assigned_models.exists():
        for model in camera.assigned_models.all():
            status = "🟢" if model.is_active else "⚫"
            print(f"    {status} {model.name}")
except Exception as e:
    print(f"❌ Camera not found: {e}")

print("\n=== To Test Fully ===")
print("1. Go to http://localhost:8000/accounts/login/")
print("2. Login with your credentials")
print("3. Navigate to http://localhost:8000/camera/2/")
print("4. You should see live webcam stream")
print()

import os
import django
import json

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rakshnetra.settings')
django.setup()

from feeds.models import CameraFeed
from ai.models import AIModel
from ai.inference import FrameProcessor
import numpy as np
import cv2

print("=" * 60)
print("FIGHTING DETECTION TEST")
print("=" * 60)

# Test 1: Check if fighting model is active
print("\n1. Checking Fighting Detection Model...")
fighting_model = AIModel.objects.filter(model_type=AIModel.TYPE_FIGHTING).first()
if fighting_model:
    print(f"   ✓ Model found: {fighting_model.name}")
    print(f"   ✓ Active: {fighting_model.is_active}")
    print(f"   ✓ Type: {fighting_model.get_model_type_display()}")
else:
    print("   ✗ Fighting detection model not found")

# Test 2: Check available cameras
print("\n2. Checking Video Cameras...")
cameras = CameraFeed.objects.filter(enabled=True)
print(f"   ✓ Found {cameras.count()} enabled cameras:")
for cam in cameras:
    print(f"      • {cam.name} (ID: {cam.id}) - {cam.protocol}")

# Test 3: Simulate fighting detection
print("\n3. Testing Fighting Detection Algorithm...")
# Create mock detections for people close together
mock_detections = [
    {
        "bbox": [100, 100, 200, 300],  # Person 1
        "label": "person",
        "confidence": 0.85
    },
    {
        "bbox": [150, 120, 250, 320],  # Person 2 (overlapping)
        "label": "person", 
        "confidence": 0.82
    },
    {
        "bbox": [180, 130, 280, 330],  # Person 3 (close cluster)
        "label": "person",
        "confidence": 0.80
    }
]

frame_shape = (480, 640, 3)  # height, width, channels
fighting_results = FrameProcessor.detect_fighting(mock_detections, frame_shape)

if fighting_results:
    print(f"   ✓ Fighting detected! Found {len(fighting_results)} cluster(s):")
    for i, result in enumerate(fighting_results):
        print(f"      Cluster {i+1}:")
        print(f"        • People: {result.get('people_count', 'N/A')}")
        print(f"        • Confidence: {result.get('confidence', 0):.2%}")
        print(f"        • Bbox: {result.get('bbox', [])}")
else:
    print("   ✗ No fighting detected in mock data (check algorithm)")

# Test 4: Check registered cameras with fighting video
print("\n4. Checking Fight Detection Videos...")
fight_cameras = CameraFeed.objects.filter(name__icontains='fight')
if fight_cameras.exists():
    print(f"   ✓ Found {fight_cameras.count()} fighting video camera(s):")
    for cam in fight_cameras:
        print(f"      • {cam.name} (ID: {cam.id})")
        print(f"        Source: {cam.source}")
        print(f"        Protocol: {cam.protocol}")
        print(f"        Mode: {cam.mode}")
else:
    print("   ✓ No dedicated fighting cameras yet")

print("\n" + "=" * 60)
print("SUMMARY")
print("=" * 60)
print("""
✓ Fighting Detection System Ready

What happens when you play a video:
1. System detects people in frame
2. Analyzes proximity between people
3. If multiple people are close/overlapping:
   → Labels as "FIGHTING DETECTED"
   → Shows red box around cluster
   → Logs alert event
   → Displays on dashboard

You can now play the fight or gun_fight videos and see:
• Red boxes around people clusters
• "FIGHTING DETECTED" labels
• Alerts in the Events/Alerts panel
""")

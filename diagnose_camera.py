#!/usr/bin/env python
"""
Diagnose why camera stream is stopping
"""

import os
import django
import cv2
import time
import psutil

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rakshnetra.settings')
django.setup()

from feeds.models import CameraFeed

def check_resources():
    """Check CPU, RAM usage"""
    print("\n📊 SYSTEM RESOURCES:")
    print(f"  CPU Usage: {psutil.cpu_percent(interval=1)}%")
    print(f"  RAM Usage: {psutil.virtual_memory().percent}%")
    print(f"  Available RAM: {psutil.virtual_memory().available / (1024**3):.2f} GB")

def test_webcam_continuous():
    """Test webcam for 30 seconds to see when it fails"""
    print("\n🎥 TESTING WEBCAM (30 second test):")
    cap = cv2.VideoCapture(0)
    
    if not cap.isOpened():
        print("❌ Webcam not accessible!")
        return
    
    print("✅ Webcam opened")
    frame_count = 0
    start_time = time.time()
    last_success = start_time
    
    try:
        while time.time() - start_time < 30:
            ret, frame = cap.read()
            if ret:
                frame_count += 1
                last_success = time.time()
                if frame_count % 30 == 0:
                    print(f"  ✓ Frames: {frame_count} ({int(time.time() - start_time)}s)")
            else:
                elapsed = time.time() - last_success
                print(f"  ❌ Frame read FAILED at frame {frame_count}, elapsed: {elapsed:.2f}s")
                break
    except Exception as e:
        print(f"  ❌ Exception: {e}")
    finally:
        cap.release()
        total_time = time.time() - start_time
        print(f"  Total: {frame_count} frames in {total_time:.2f}s ({frame_count/total_time:.1f} fps)")

def check_camera_config():
    """Check camera in database"""
    print("\n📹 CAMERA CONFIGURATION:")
    try:
        camera = CameraFeed.objects.get(id=2)
        print(f"  ✓ Camera: {camera.name}")
        print(f"  - Protocol: {camera.protocol}")
        print(f"  - Source: {camera.source}")
        print(f"  - Enabled: {camera.enabled}")
        print(f"  - Active models: {camera.assigned_models.count()}")
    except Exception as e:
        print(f"  ❌ Error: {e}")

def main():
    print("\n" + "="*60)
    print("RAKSHNETRA CAMERA DIAGNOSTICS")
    print("="*60)
    
    check_resources()
    check_camera_config()
    test_webcam_continuous()
    
    print("\n" + "="*60)
    print("DIAGNOSIS COMPLETE")
    print("="*60)
    
    print("""
POSSIBLE FIXES:

1. RAM Low? Check if available RAM > 500MB
   → Close other apps
   → Restart server: Ctrl+C then python manage.py runserver

2. Webcam Dropped? 
   → Check if another app using webcam
   → Restart webcam: unplug/replug or reboot

3. Inference Too Slow?
   → Deactivate models (if any are active)
   → Use simpler model or lower resolution

4. Browser Issue?
   → Refresh page: F5
   → Try different browser
   → Check browser console: F12 → Console
    """)

if __name__ == '__main__':
    main()

#!/usr/bin/env python
"""
Setup script: Create a webcam camera feed and show where to upload AI models.
Run this from the project root: python setup_webcam.py
"""

import os
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rakshnetra.settings')
django.setup()

from feeds.models import CameraFeed
from ai.models import AIModel
from django.conf import settings

def main():
    print("\n" + "="*70)
    print("RAKSHNETRA: Webcam & AI Model Setup")
    print("="*70)
    
    # 1. Create or get webcam camera
    camera, created = CameraFeed.objects.get_or_create(
        name="Webcam Feed",
        defaults={
            'protocol': CameraFeed.PROTO_WEBCAM,
            'source': '0',  # Device index 0 = default webcam
            'mode': CameraFeed.MODE_AI,
            'enabled': True
        }
    )
    
    if created:
        print(f"\n✓ Created webcam camera: '{camera.name}' (ID: {camera.id})")
        print(f"  - Protocol: {camera.get_protocol_display()}")
        print(f"  - Source: {camera.source}")
        print(f"  - Mode: {camera.get_mode_display()}")
    else:
        print(f"\n✓ Webcam camera already exists: '{camera.name}' (ID: {camera.id})")
    
    # 2. Show model upload info
    print("\n" + "-"*70)
    print("AI MODEL UPLOAD LOCATION:")
    print("-"*70)
    print(f"\n📁 Upload your .pt files here:")
    print(f"   Web UI: http://localhost:8000/manage/models/")
    print(f"   Files save to: {settings.MEDIA_ROOT / 'models'}/")
    
    # 3. Show how to assign models to camera
    print("\n" + "-"*70)
    print("WORKFLOW:")
    print("-"*70)
    print(f"""
1. Start the dev server:
   python manage.py runserver
   
2. Open browser and log in:
   http://localhost:8000/accounts/login/
   
3. Upload your .pt model:
   http://localhost:8000/manage/models/
   - Click "+ Upload Model"
   - Select model type (e.g., "Weapon Detection")
   - Upload your .pt file
   - Set confidence threshold (e.g., 0.5)
   - Click "Upload Model"
   
4. Activate the model:
   - On the Models page, click the "Activate" button on your model card
   
5. Assign model to webcam camera:
   - Go to Camera Management: http://localhost:8000/manage/cameras/
   - Click "Edit" on the "{camera.name}" camera (ID: {camera.id})
   - Under "Assign AI Models", check your model
   - Click "Save Camera"
   
6. View live detection:
   - Click "👁 View Live" on the camera card
   - Or go directly to: http://localhost:8000/camera/{camera.id}/
   - You should see your webcam with detection boxes overlaid
""")
    
    # 4. List existing models
    models = AIModel.objects.all()
    if models.exists():
        print("-"*70)
        print("EXISTING MODELS IN DATABASE:")
        print("-"*70)
        for model in models:
            status = "🟢 ACTIVE" if model.is_active else "⚫ INACTIVE"
            file_status = "📄 Yes" if model.model_file else "❌ No file"
            print(f"\n  {status} | {model.name}")
            print(f"     Type: {model.get_model_type_display()}")
            print(f"     File: {file_status}")
            if model.model_file:
                print(f"     Path: {model.model_file.path}")
            print(f"     Threshold: {model.confidence_threshold}")
    
    # 5. Test webcam
    print("\n" + "-"*70)
    print("TEST WEBCAM CONNECTION:")
    print("-"*70)
    try:
        import cv2
        cap = cv2.VideoCapture(0)
        if cap.isOpened():
            print("✓ Webcam (device 0) is accessible!")
            ret, frame = cap.read()
            if ret:
                print(f"  Frame size: {frame.shape}")
            cap.release()
        else:
            print("❌ Webcam device 0 not accessible")
            print("   Try: python setup_webcam.py --test-devices")
    except Exception as e:
        print(f"❌ OpenCV error: {e}")
    
    print("\n" + "="*70)
    print("Setup complete! Now go to http://localhost:8000 to get started.")
    print("="*70 + "\n")

if __name__ == "__main__":
    main()

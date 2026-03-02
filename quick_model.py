#!/usr/bin/env python
"""
Quick model management script for testing
- Upload a model file
- Activate it
- Assign to webcam
"""

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rakshnetra.settings')
django.setup()

from ai.models import AIModel
from feeds.models import CameraFeed
from django.core.files.base import File

def upload_model(file_path, name, model_type, threshold=0.5):
    """Upload a model programmatically"""
    if not os.path.exists(file_path):
        print(f"❌ File not found: {file_path}")
        return None
    
    if not name:
        name = os.path.splitext(os.path.basename(file_path))[0]
    
    print(f"\n📤 Uploading model: {name}")
    print(f"   File: {file_path}")
    print(f"   Type: {model_type}")
    
    try:
        model = AIModel.objects.create(
            name=name,
            model_type=model_type,
            is_active=False,
            confidence_threshold=threshold,
            description=f"Uploaded from: {file_path}"
        )
        
        with open(file_path, 'rb') as f:
            model.model_file.save(
                os.path.basename(file_path),
                File(f),
                save=True
            )
        
        print(f"✓ Model uploaded successfully!")
        print(f"  - ID: {model.id}")
        print(f"  - Path: {model.model_file.path}")
        return model
    except Exception as e:
        print(f"❌ Upload failed: {e}")
        return None

def activate_model(model_id):
    """Activate a model"""
    try:
        model = AIModel.objects.get(id=model_id)
        model.is_active = True
        model.save()
        print(f"✓ Model '{model.name}' activated!")
        return model
    except AIModel.DoesNotExist:
        print(f"❌ Model ID {model_id} not found")
        return None

def assign_to_camera(model_id, camera_id=2):
    """Assign model to camera"""
    try:
        model = AIModel.objects.get(id=model_id)
        camera = CameraFeed.objects.get(id=camera_id)
        camera.assigned_models.add(model)
        print(f"✓ Model '{model.name}' assigned to camera '{camera.name}'")
        return camera
    except Exception as e:
        print(f"❌ Assignment failed: {e}")
        return None

def list_models():
    """List all models"""
    models = AIModel.objects.all()
    if not models:
        print("No models found")
        return
    
    print("\n📋 Available Models:")
    for m in models:
        status = "🟢" if m.is_active else "⚫"
        has_file = "📄" if m.model_file else "❌"
        print(f"\n  {status} {m.name} (ID: {m.id})")
        print(f"     Type: {m.get_model_type_display()}")
        print(f"     File: {has_file}")
        if m.model_file:
            print(f"     Path: {m.model_file.path}")
        
        # Show assigned cameras
        cameras = CameraFeed.objects.filter(assigned_models=m)
        if cameras:
            print(f"     Cameras: {', '.join([c.name for c in cameras])}")

def main():
    if len(sys.argv) < 2:
        print("""
Usage:
  python quick_model.py upload <file_path> <name> <type> [threshold]
  python quick_model.py activate <model_id>
  python quick_model.py assign <model_id> [camera_id]
  python quick_model.py list
  
Examples:
  python quick_model.py upload "C:/path/to/model.pt" "My YOLOv8" weapon_detection 0.5
  python quick_model.py activate 1
  python quick_model.py assign 1 2
  python quick_model.py list
        """)
        return
    
    cmd = sys.argv[1].lower()
    
    if cmd == 'upload':
        if len(sys.argv) < 5:
            print("Usage: python quick_model.py upload <file> <name> <type> [threshold]")
            return
        file_path = sys.argv[2]
        name = sys.argv[3]
        model_type = sys.argv[4]
        threshold = float(sys.argv[5]) if len(sys.argv) > 5 else 0.5
        model = upload_model(file_path, name, model_type, threshold)
        if model:
            print(f"\n💡 Next step: python quick_model.py activate {model.id}")
    
    elif cmd == 'activate':
        if len(sys.argv) < 3:
            print("Usage: python quick_model.py activate <model_id>")
            return
        model_id = int(sys.argv[2])
        model = activate_model(model_id)
        if model:
            print(f"💡 Next step: python quick_model.py assign {model.id}")
    
    elif cmd == 'assign':
        if len(sys.argv) < 3:
            print("Usage: python quick_model.py assign <model_id> [camera_id]")
            return
        model_id = int(sys.argv[2])
        camera_id = int(sys.argv[3]) if len(sys.argv) > 3 else 2
        camera = assign_to_camera(model_id, camera_id)
        if camera:
            print(f"💡 Next step: Open http://localhost:8000/camera/{camera.id}/")
    
    elif cmd == 'list':
        list_models()
    
    else:
        print(f"Unknown command: {cmd}")

if __name__ == '__main__':
    main()

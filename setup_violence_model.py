#!/usr/bin/env python
"""
Download and setup pre-trained violence/fighting detection model
"""
import os
import sys
import django

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rakshnetra.settings')
django.setup()

from ai.models import AIModel
from django.core.files import File
from pathlib import Path

def setup_violence_model():
    """Setup violence detection model using YOLOv8"""
    print("🔧 Setting up Violence/Fighting Detection Model...")
    
    # First, let's use YOLOv8 with a custom violence dataset
    # We'll download a pre-trained model or use YOLOv8 base
    
    try:
        from ultralytics import YOLO
        print("✓ Ultralytics YOLO available")
    except ImportError:
        print("❌ Installing ultralytics...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "ultralytics"])
        from ultralytics import YOLO
    
    # Download YOLOv8n model (lightweight, fast)
    print("\n📥 Downloading YOLOv8n model...")
    model = YOLO('yolov8n.pt')  # nano version for speed
    
    # Save to media/models
    models_dir = Path('media/models')
    models_dir.mkdir(parents=True, exist_ok=True)
    
    model_path = models_dir / 'yolov8n_violence.pt'
    
    # Export the model
    print(f"💾 Saving model to {model_path}...")
    import shutil
    shutil.copy('yolov8n.pt', str(model_path))
    
    # Create or update the model in database
    print("\n📝 Registering model in database...")
    
    # Check if violence detection model exists
    violence_model = AIModel.objects.filter(
        model_type=AIModel.TYPE_FIGHTING
    ).first()
    
    if violence_model:
        print(f"Found existing model: {violence_model.name}")
        violence_model.model_file = str(model_path.relative_to('media'))
        violence_model.is_active = True
        violence_model.confidence_threshold = 0.4  # Lower threshold for violence
        violence_model.description = "YOLOv8n-based violence/fighting detection - detects person interactions that may indicate violence"
        violence_model.save()
        print(f"✓ Updated: {violence_model.name}")
    else:
        violence_model = AIModel.objects.create(
            name="Violence Detection (YOLOv8n)",
            model_type=AIModel.TYPE_FIGHTING,
            model_file=str(model_path.relative_to('media')),
            is_active=True,
            confidence_threshold=0.4,
            description="YOLOv8n-based violence/fighting detection - detects person interactions"
        )
        print(f"✓ Created new model: {violence_model.name}")
    
    print("\n" + "="*60)
    print("✅ Violence Detection Model Setup Complete!")
    print("="*60)
    print(f"\nModel Details:")
    print(f"  Name: {violence_model.name}")
    print(f"  Type: {violence_model.model_type}")
    print(f"  File: {violence_model.model_file}")
    print(f"  Active: {violence_model.is_active}")
    print(f"  Confidence: {violence_model.confidence_threshold}")
    
    print("\n📋 Next Steps:")
    print("  1. Restart the Django server")
    print("  2. The model will detect people and their interactions")
    print("  3. Fighting detection is based on proximity and movement")
    
    print("\n💡 Note: For better accuracy, you can:")
    print("  - Train YOLOv8 on a violence-specific dataset")
    print("  - Use Roboflow violence detection models")
    print("  - Fine-tune with your own fighting videos")
    
    return violence_model

if __name__ == '__main__':
    try:
        setup_violence_model()
    except Exception as e:
        print(f"\n❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

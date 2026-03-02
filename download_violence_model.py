#!/usr/bin/env python
"""
Alternative: Download a specialized violence detection model from Roboflow
For better accuracy than general YOLOv8
"""
import os
import sys

print("""
╔══════════════════════════════════════════════════════════╗
║     Enhanced Violence Detection Model Options           ║
╚══════════════════════════════════════════════════════════╝

The current setup uses YOLOv8n to detect persons, then applies
rule-based logic to identify fighting based on proximity.

For BETTER accuracy, you can:

1. 🎯 Use Roboflow Violence Detection Dataset
   - Visit: https://universe.roboflow.com/
   - Search for "violence detection" or "fighting detection"
   - Download a pre-trained model
   - Example datasets:
     * Violence Detection (boxing, fighting, normal)
     * Fight Detection Dataset
     * Weapon and Violence Detection

2. 🔧 Train Your Own Model
   - Collect fighting/violence videos
   - Label them using Roboflow or LabelImg
   - Train YOLOv8 on your custom dataset
   
3. 📦 Use Pre-trained Action Recognition
   - Download from: https://github.com/topics/violence-detection
   - Popular models:
     * I3D (Inflated 3D ConvNet)
     * SlowFast
     * TimeSformer

═══════════════════════════════════════════════════════════

📋 CURRENT SETUP STATUS:
✓ YOLOv8n model installed for person detection
✓ Rule-based fighting detection enabled
✓ Sensitivity improved for better detection

💡 NEXT STEPS TO IMPROVE:
1. Test with your fighting videos
2. Adjust confidence threshold (currently 0.4)
3. Fine-tune proximity and overlap thresholds
4. Optional: Replace with specialized violence model

═══════════════════════════════════════════════════════════
""")

print("\n🔗 Quick Links:")
print("  • Roboflow: https://universe.roboflow.com/search?q=violence")
print("  • GitHub Violence Models: https://github.com/topics/violence-detection")
print("  • Ultralytics Hub: https://hub.ultralytics.com/")

print("\n" + "="*60)
choice = input("\nWould you like instructions to add a Roboflow model? (y/n): ").strip().lower()

if choice == 'y':
    print("""
    
📖 HOW TO ADD A ROBOFLOW MODEL:

1. Go to: https://universe.roboflow.com/
2. Search for "violence detection" or "fighting detection"
3. Choose a dataset and click "Download Dataset"
4. Select "YOLOv8" format
5. Download the model weights (.pt file)
6. Copy the .pt file to: media/models/
7. Run this command:

   python manage.py shell
   
   Then in the shell:
   
   from ai.models import AIModel
   model = AIModel.objects.get(model_type='fighting_violence_detection')
   model.model_file = 'models/your_violence_model.pt'
   model.confidence_threshold = 0.5  # Adjust as needed
   model.save()
   exit()

8. Restart the server

That's it! Your violence detection will now use the specialized model.
""")
else:
    print("\n✓ Okay! The current setup will work with improved sensitivity.")
    print("  Test it with your videos and adjust thresholds as needed.")

print("\n" + "="*60)
print("Done!")

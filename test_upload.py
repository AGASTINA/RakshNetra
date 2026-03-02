#!/usr/bin/env python
"""
Test script to verify model upload functionality end-to-end.
"""
import os
import sys
import django
from io import BytesIO

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rakshnetra.settings')
sys.path.insert(0, r'c:\Workspace\RakshNetra')
django.setup()

from django.core.files.uploadedfile import SimpleUploadedFile
from ai.models import AIModel

# Create a dummy PyTorch-like file
dummy_file_content = b'\x80\x02\x00\x00\x00\x00\x00\x00\x00'  # Dummy binary content
dummy_file = SimpleUploadedFile(
    "test_model.pt",
    dummy_file_content,
    content_type="application/octet-stream"
)

# Create a model with the file
model = AIModel.objects.create(
    name="Test Model Upload",
    model_type="pytorch",
    confidence_threshold=0.75,
    description="Test model for upload verification"
)

# Save the file
model.model_file.save(dummy_file.name, dummy_file)
model.save()

print(f"✓ Model created: {model.name} (ID: {model.id})")
print(f"✓ File saved to: {model.model_file.name}")
print(f"✓ File path: {model.model_file.path}")
print(f"✓ File exists: {os.path.exists(model.model_file.path)}")
print(f"✓ File size: {os.path.getsize(model.model_file.path)} bytes")

# List all models
all_models = AIModel.objects.all()
print(f"\n✓ Total models in DB: {all_models.count()}")
for m in all_models:
    print(f"  - {m.name} ({m.model_type}): {m.model_file.name if m.model_file else 'NO FILE'}")

# Verify media/models directory
media_models_dir = r'c:\Workspace\RakshNetra\media\models'
print(f"\n✓ Media/models directory exists: {os.path.isdir(media_models_dir)}")
print(f"✓ Files in media/models:")
if os.path.isdir(media_models_dir):
    for f in os.listdir(media_models_dir):
        print(f"  - {f}")

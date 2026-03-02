#!/usr/bin/env python
"""
Register face images in the database for face recognition
"""
import os
import sys
import django
from pathlib import Path

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rakshnetra.settings')
django.setup()

from ai.models import FaceIdentity
from django.core.files import File

def register_faces():
    """Register Modi and Draupadi Murmu faces for recognition"""
    
    print("📸 Registering Face Identities...")
    print("="*60)
    
    face_data = [
        # Modi - Prime Minister (VIP)
        {
            'images': ['modi1.jpg', 'modi_3.jpg', 'modi_4.jpg'],
            'label': 'Narendra Modi',
            'identity_type': FaceIdentity.IDENTITY_VIP,
            'position': 'Prime Minister of India',
            'description': 'Prime Minister of India, BJP Leader'
        },
        # Draupadi Murmu - President (VIP)
        {
            'images': ['draupathi_murmur.jpeg', 'draupathi_murmur1.jpg', 'draupathi_murmur3.jpg'],
            'label': 'Draupadi Murmu',
            'identity_type': FaceIdentity.IDENTITY_VIP,
            'position': 'President of India',
            'description': 'President of India'
        }
    ]
    
    vip_folder = Path('media/face_identities/vip')
    
    for face_group in face_data:
        label = face_group['label']
        
        # Check if already registered
        existing = FaceIdentity.objects.filter(label=label).first()
        
        if existing:
            print(f"\n⚠️  {label} already registered")
            print(f"   Position: {existing.position}")
            print(f"   Type: {existing.identity_type}")
            continue
        
        # Use first image as the main one
        first_image = face_group['images'][0]
        image_path = vip_folder / first_image
        
        if not image_path.exists():
            print(f"\n❌ Image not found: {first_image}")
            continue
        
        try:
            # Create FaceIdentity record
            face_identity = FaceIdentity(
                label=label,
                identity_type=face_group['identity_type'],
                position=face_group['position'],
                description=face_group['description']
            )
            
            # Attach the image
            with open(image_path, 'rb') as f:
                face_identity.face_image.save(
                    first_image,
                    File(f),
                    save=False
                )
            
            face_identity.save()
            
            print(f"\n✅ Registered: {label}")
            print(f"   Position: {face_group['position']}")
            print(f"   Type: {face_group['identity_type']}")
            print(f"   Image: {first_image}")
            print(f"   Description: {face_group['description']}")
            
        except Exception as e:
            print(f"\n❌ Error registering {label}: {e}")
            import traceback
            traceback.print_exc()
    
    print("\n" + "="*60)
    print("✅ Face registration complete!")
    print("\n📋 Registered Faces:")
    
    for face in FaceIdentity.objects.all():
        print(f"\n  🔹 {face.label}")
        print(f"     Type: {face.get_identity_type_display()}")
        print(f"     Position: {face.position}")
        print(f"     Image: {face.face_image}")
    
    print("\n" + "="*60)
    print("💡 Face recognition will now:")
    print("   • Detect and identify Modi and Draupadi Murmu")
    print("   • Mark them as VIP in the dashboard")
    print("   • Show their names and positions")
    print("   • Create alerts when they appear on camera")
    print("\n✓ Ready to restart the server!")

if __name__ == '__main__':
    try:
        register_faces()
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)

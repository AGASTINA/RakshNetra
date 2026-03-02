import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rakshnetra.settings')
django.setup()

from django.test import Client
from accounts.models import User

# Create a test client
client = Client()

try:
    # Login
    user, created = User.objects.get_or_create(username='testuser', defaults={
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test@example.com'
    })
    if created:
        user.set_password('testpass123')
        user.save()
    
    client.login(username='testuser', password='testpass123')
    
    # Test video file access
    print("=== Testing Video File Access ===\n")
    
    video_paths = [
        '/media/draupathi_murmur.mp4',
        '/media/videos/draupathi_murmur.mp4',
    ]
    
    for path in video_paths:
        response = client.get(path)
        status = '✓' if response.status_code == 200 else '✗'
        print(f"{status} {path}: {response.status_code}")
        if response.status_code == 200:
            # For streaming responses, check the content-type header instead
            content_type = response.get('Content-Type', 'Unknown')
            print(f"   Content-Type: {content_type}")
    
    # Check file exists on disk
    print("\n=== Checking Files on Disk ===\n")
    
    file_paths = [
        'media/draupathi_murmur.mp4',
        'media/videos/draupathi_murmur.mp4',
    ]
    
    for path in file_paths:
        full_path = os.path.join('c:\\Users\\agast\\OneDrive\\Desktop\\RakshNetra', path)
        exists = os.path.exists(full_path)
        status = '✓' if exists else '✗'
        print(f"{status} {path}: {'EXISTS' if exists else 'NOT FOUND'}")
        if exists:
            size = os.path.getsize(full_path)
            print(f"   Size: {size:,} bytes ({size / 1024 / 1024:.2f} MB)")
            
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

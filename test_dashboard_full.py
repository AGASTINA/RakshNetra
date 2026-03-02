import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rakshnetra.settings')
django.setup()

from django.test import Client
from accounts.models import User
from feeds.models import CameraFeed
from events.models import Event
from ai.models import AIModel

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
    
    print("=" * 60)
    print("RAKSHNETRA DASHBOARD - FINAL VERIFICATION")
    print("=" * 60)
    
    # Test 1: Dashboard rendering
    print("\n1. Dashboard Rendering")
    print("-" * 40)
    response = client.get('/')
    if response.status_code == 200:
        html = response.content.decode('utf-8')
        print("✓ Dashboard loads (HTTP 200)")
        print(f"  HTML size: {len(html):,} bytes")
    else:
        print(f"✗ Dashboard failed: {response.status_code}")
    
    # Test 2: Database counts
    print("\n2. Database Content")
    print("-" * 40)
    cameras = CameraFeed.objects.all()
    events = Event.objects.all()
    models = AIModel.objects.all()
    active_models = AIModel.objects.filter(is_active=True)
    
    print(f"✓ Cameras: {cameras.count()} total")
    for cam in cameras:
        print(f"    • {cam.name} ({cam.protocol})")
        if cam.protocol == 'file':
            print(f"      Source: {cam.source}")
    
    print(f"✓ Events: {events.count()} total")
    for evt in events[:3]:  # Show first 3
        print(f"    • {evt.name} ({evt.threat_level})")
    
    print(f"✓ AI Models: {models.count()} total, {active_models.count()} active")
    for model in active_models[:3]:
        print(f"    • {model.name} ({'ACTIVE' if model.is_active else 'INACTIVE'})")
    
    # Test 3: Video file
    print("\n3. Video File")
    print("-" * 40)
    draupathi_cam = cameras.filter(name='president').first()
    if draupathi_cam:
        print(f"✓ Found 'president' camera")
        print(f"  Protocol: {draupathi_cam.protocol}")
        print(f"  Source: {draupathi_cam.source}")
        
        # Check if file exists
        if draupathi_cam.source:
            full_path = os.path.join('c:\\Users\\agast\\OneDrive\\Desktop\\RakshNetra', 
                                    draupathi_cam.source)
            if os.path.exists(full_path):
                size = os.path.getsize(full_path)
                print(f"  ✓ Video file exists ({size / 1024 / 1024:.2f} MB)")
            else:
                print(f"  ✗ Video file not found")
    else:
        print("✗ 'president' camera not found")
    
    # Test 4: API endpoints
    print("\n4. API Endpoints")
    print("-" * 40)
    endpoints = [
        '/api/cameras/',
        '/api/events/',
        '/api/models/',
    ]
    
    for endpoint in endpoints:
        response = client.get(endpoint)
        status = '✓' if response.status_code == 200 else '✗'
        print(f"{status} {endpoint}: {response.status_code}")
    
    # Test 5: HTML template elements
    print("\n5. Template Elements")
    print("-" * 40)
    response = client.get('/')
    html = response.content.decode('utf-8')
    
    elements = {
        'Header/Title': '<title>RakshNetra' in html,
        'Event Selector': 'event-select' in html,
        'Video Grid': 'video-grid' in html,
        'Models Section': 'Active Models' in html,
        'Dashboard Data': 'window.dashboardData' in html,
        'Video Player': 'video-control-btn' in html,
        'Situational Map': 'situational-map' in html,
    }
    
    for element, found in elements.items():
        status = '✓' if found else '✗'
        print(f"{status} {element}")
    
    print("\n" + "=" * 60)
    print("VERIFICATION COMPLETE")
    print("=" * 60)
    
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

import os
import sys
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rakshnetra.settings')
django.setup()

from django.test import Client
from accounts.models import User

# Create a test client
client = Client()

# Try to login first (since Dashboard requires login)
try:
    # Create a test user if it doesn't exist
    user, created = User.objects.get_or_create(username='testuser', defaults={
        'first_name': 'Test',
        'last_name': 'User',
        'email': 'test@example.com'
    })
    if created:
        user.set_password('testpass123')
        user.save()
    
    # Login
    login_success = client.login(username='testuser', password='testpass123')
    print(f"Login: {'✓ Success' if login_success else '✗ Failed'}")
    
    # Test dashboard endpoint
    response = client.get('/')
    
    print(f"\n=== Dashboard Response ===")
    print(f"Status Code: {response.status_code}")
    
    if response.status_code == 200:
        # Check if critical parts are in the response
        html = response.content.decode('utf-8')
        
        checks = {
            '✓ Title': '<title>RakshNetra' in html,
            '✓ Event Selector': 'event-select' in html,
            '✓ Camera List': 'video-grid' in html,
            '✓ Dashboard Data': 'window.dashboardData' in html,
            '✓ Models Section': 'Active Models' in html
        }
        
        print("\nTemplate Elements:")
        for check, passed in checks.items():
            print(f"  {check}: {'FOUND' if passed else 'MISSING'}")
            
        # Check for JSON errors
        if 'dashboardData' in html:
            start_idx = html.find('window.dashboardData = {')
            if start_idx > 0:
                end_idx = html.find('};', start_idx) + 2
                if end_idx > start_idx:
                    json_snippet = html[start_idx:end_idx]
                    print(f"\n✓ Dashboard data script found")
                    print(f"  JSON length: {len(json_snippet)} characters")
        
        print("\n✓ Dashboard rendered successfully!")
    else:
        print(f"Error: {response.status_code}")
        if response.status_code >= 400:
            print("Content:", response.content.decode('utf-8')[:500])
            
except Exception as e:
    print(f"✗ Error: {e}")
    import traceback
    traceback.print_exc()

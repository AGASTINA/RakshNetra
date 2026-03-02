#!/usr/bin/env python
"""
RakshNetra API Test Script
Test various API endpoints to verify system is working
"""

import requests
import json
import sys

BASE_URL = "http://localhost:8000"

class APITester:
    def __init__(self):
        self.session = requests.Session()
        self.token = None
        
    def signup(self, username, email, password, role="viewer"):
        """Create a new user"""
        print(f"\n📝 Creating user: {username}")
        url = f"{BASE_URL}/accounts/signup/"
        data = {
            'username': username,
            'email': email,
            'password1': password,
            'password2': password,
            'role': role
        }
        try:
            # Note: signup redirects on success, so we check for 200-399 status
            response = self.session.post(url, data=data, allow_redirects=False)
            if 200 <= response.status_code < 400:
                print(f"✅ User created successfully!")
                return True
        except Exception as e:
            print(f"❌ Error: {e}")
        return False
    
    def login(self, username, password):
        """Login user"""
        print(f"\n🔐 Logging in: {username}")
        url = f"{BASE_URL}/accounts/login/"
        data = {
            'username': username,
            'password': password
        }
        try:
            response = self.session.post(url, data=data, allow_redirects=False)
            if response.status_code == 302:  # Redirect on success
                print(f"✅ Login successful!")
                return True
        except Exception as e:
            print(f"❌ Error: {e}")
        return False
    
    def test_cameras_api(self):
        """Test camera API endpoints"""
        print(f"\n📹 Testing Camera APIs")
        
        # Get protocols
        url = f"{BASE_URL}/api/cameras/protocols/"
        response = self.session.get(url)
        if response.status_code == 200:
            print(f"✅ Available protocols: {response.json()}")
        else:
            print(f"❌ Failed to get protocols: {response.status_code}")
        
        # Get modes
        url = f"{BASE_URL}/api/cameras/modes/"
        response = self.session.get(url)
        if response.status_code == 200:
            print(f"✅ Available modes: {response.json()}")
        else:
            print(f"❌ Failed to get modes: {response.status_code}")
        
        # List cameras
        url = f"{BASE_URL}/api/cameras/"
        response = self.session.get(url)
        if response.status_code == 200:
            cameras = response.json()
            if isinstance(cameras, dict) and 'results' in cameras:
                cameras = cameras['results']
            print(f"✅ Found {len(cameras)} cameras")
            for camera in cameras:
                print(f"   - {camera.get('name', 'Unknown')} ({camera.get('protocol', 'unknown')})")
        else:
            print(f"❌ Failed to list cameras: {response.status_code}")
    
    def test_models_api(self):
        """Test AI model API endpoints"""
        print(f"\n🤖 Testing AI Model APIs")
        
        # Get model types
        url = f"{BASE_URL}/api/ai/models/types/"
        response = self.session.get(url)
        if response.status_code == 200:
            types = response.json()
            print(f"✅ Available model types:")
            for mtype in types:
                print(f"   - {mtype.get('label')}")
        else:
            print(f"❌ Failed to get model types: {response.status_code}")
        
        # List active models
        url = f"{BASE_URL}/api/ai/models/active/"
        response = self.session.get(url)
        if response.status_code == 200:
            models = response.json()
            if isinstance(models, dict) and 'results' in models:
                models = models['results']
            print(f"✅ Found {len(models)} active models")
            for model in models:
                print(f"   - {model.get('name', 'Unknown')}")
        else:
            print(f"❌ Failed to list models: {response.status_code}")
    
    def test_alerts_api(self):
        """Test alerts API endpoints"""
        print(f"\n🚨 Testing Alert APIs")
        
        # Get severity levels
        url = f"{BASE_URL}/api/alerts/severities/"
        response = self.session.get(url)
        if response.status_code == 200:
            severities = response.json()
            print(f"✅ Alert severity levels:")
            for sev in severities:
                print(f"   - {sev.get('label')}")
        else:
            print(f"❌ Failed to get severity levels: {response.status_code}")
        
        # Get recent alerts
        url = f"{BASE_URL}/api/alerts/recent/"
        response = self.session.get(url)
        if response.status_code == 200:
            alerts = response.json()
            if isinstance(alerts, dict) and 'results' in alerts:
                alerts = alerts['results']
            print(f"✅ Found {len(alerts)} recent alerts")
            for alert in alerts[:3]:
                print(f"   - {alert.get('threat_type')} ({alert.get('severity')})")
        else:
            print(f"❌ Failed to get alerts: {response.status_code}")
    
    def test_dashboard(self):
        """Test dashboard access"""
        print(f"\n🎛️  Testing Dashboard")
        url = f"{BASE_URL}/"
        response = self.session.get(url)
        if response.status_code == 200:
            print(f"✅ Dashboard accessible")
        elif response.status_code == 302:
            print(f"✅ Dashboard accessible (redirected - need login)")
        else:
            print(f"❌ Dashboard error: {response.status_code}")

def main():
    print("="*60)
    print("🔍 RakshNetra API Test Suite")
    print("="*60)
    
    tester = APITester()
    
    # Create test user
    test_user = "testuser"
    test_email = "test@example.com"
    test_password = "TestPassword123456"
    
    # Try to signup (may fail if user exists, which is OK)
    print("\nAttempting to create test user...")
    tester.signup(test_user, test_email, test_password, "operator")
    
    # Login
    if not tester.login(test_user, test_password):
        print("\n❌ Could not login. Make sure to create account first at http://localhost:8000/accounts/signup/")
        return
    
    # Test various endpoints
    tester.test_dashboard()
    tester.test_cameras_api()
    tester.test_models_api()
    tester.test_alerts_api()
    
    print("\n" + "="*60)
    print("✅ API Test Complete!")
    print("="*60)
    print("\n📍 Next Steps:")
    print("   1. Visit http://localhost:8000/ to access the dashboard")
    print("   2. Go to 'Cameras' to add your first camera")
    print("   3. Go to 'AI Models' to upload a model")
    print("   4. Monitor alerts in real-time")
    print("\n📚 Documentation: Check DEVELOPMENT_GUIDE.md for details")

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n\n⛔ Test interrupted by user")
        sys.exit(0)
    except Exception as e:
        print(f"\n\n❌ Unexpected error: {e}")
        sys.exit(1)

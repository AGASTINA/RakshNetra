#!/usr/bin/env python
"""
Upload detected video to RakshNetra Dashboard
Process: Video Detection -> Dashboard Upload -> Event Creation
"""

import os
import sys
import json
import requests
from pathlib import Path

# Configuration
VIDEO_FILE = 'detection_results/detected_video.mp4'
REPORT_FILE = 'detection_results/detection_report.json'
API_URL = 'http://127.0.0.1:8000/api/events/upload_detected_video/'

# Credentials (use environment variables in production)
USERNAME = 'admin'
PASSWORD = 'password'  # Change this to actual password

def get_auth_token(username, password):
    """Authenticate and get token"""
    try:
        print("🔐 Authenticating...")
        # First, try to login via token endpoint if available
        response = requests.post(
            'http://127.0.0.1:8000/api/token/',
            json={'username': username, 'password': password}
        )
        if response.status_code == 200:
            print("✅ Authentication successful")
            return response.json().get('access')
        else:
            print("⚠️  Token endpoint not available, will try without auth")
            return None
    except Exception as e:
        print(f"⚠️  Auth error: {e}")
        return None

def upload_video(video_path, report_path=None):
    """Upload video to dashboard"""
    
    if not os.path.exists(video_path):
        print(f"❌ Video file not found: {video_path}")
        return False
    
    print(f"\n📤 Uploading Video to Dashboard")
    print("=" * 70)
    print(f"Video: {video_path}")
    
    # Get file size
    file_size_mb = os.path.getsize(video_path) / (1024*1024)
    print(f"Size: {file_size_mb:.2f} MB")
    
    # Load report if available
    report_data = None
    if report_path and os.path.exists(report_path):
        try:
            with open(report_path, 'r') as f:
                report_data = json.load(f)
                print(f"📊 Detection report loaded")
        except Exception as e:
            print(f"⚠️  Could not load report: {e}")
    
    # Get authentication token
    token = get_auth_token(USERNAME, PASSWORD)
    
    # Prepare upload
    headers = {}
    if token:
        headers['Authorization'] = f'Bearer {token}'
    
    # Prepare form data
    files = {
        'video_file': open(video_path, 'rb'),
    }
    
    data = {
        'event_name': 'President Droupadi Murmu - Naval Event Detection',
        'location': 'Visakhapatnam Naval Station',
        'threat_level': 'medium',
    }
    
    # Add report if available
    if report_data:
        data['report_json'] = json.dumps(report_data)
    
    try:
        print(f"\n🚀 Uploading to: {API_URL}")
        response = requests.post(
            API_URL,
            files=files,
            data=data,
            headers=headers,
            timeout=300  # 5 minute timeout for large file
        )
        
        files['video_file'].close()
        
        print(f"Response Status: {response.status_code}")
        
        if response.status_code in [200, 201]:
            print("✅ Upload successful!")
            result = response.json()
            print(f"\n📋 Event Details:")
            print(f"   Event ID: {result.get('event', {}).get('id')}")
            print(f"   Event Name: {result.get('event', {}).get('name')}")
            print(f"   Location: {result.get('event', {}).get('location')}")
            print(f"   Threat Level: {result.get('event', {}).get('threat_level')}")
            
            video_url = result.get('video_url')
            if video_url:
                print(f"\n🎬 Video URL: {video_url}")
                print(f"📁 View in Dashboard: http://127.0.0.1:8000/events/")
            
            return True
        else:
            print(f"❌ Upload failed with status {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except requests.exceptions.ConnectionError:
        print("❌ Cannot connect to server")
        print("⚠️  Make sure Django server is running: python manage.py runserver")
        return False
    except Exception as e:
        print(f"❌ Upload error: {e}")
        return False

def main():
    """Main entry point"""
    print("\n" + "=" * 70)
    print("📤 RAKSHNETRA - VIDEO UPLOAD TO DASHBOARD")
    print("=" * 70)
    
    # Upload video
    success = upload_video(VIDEO_FILE, REPORT_FILE)
    
    if success:
        print("\n✅ Upload Complete!")
        print("\n🌐 Next Steps:")
        print("   1. Go to: http://127.0.0.1:8000/events/")
        print("   2. Find 'President Droupadi Murmu - Naval Event Detection'")
        print("   3. Watch annotated video with all detections")
        print("   4. View detection statistics and alerts")
    else:
        print("\n⚠️  Upload failed. Please check:")
        print("   1. Django server is running")
        print("   2. Video file exists at: detection_results/detected_video.mp4")
        print("   3. Database migrations are applied")
    
    print("=" * 70)

if __name__ == '__main__':
    main()

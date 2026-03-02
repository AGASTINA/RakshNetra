import urllib.request
import time
import re

time.sleep(2)

try:
    # Get the login page
    response = urllib.request.urlopen('http://127.0.0.1:8000/accounts/login/')
    html = response.read().decode('utf-8')
    print("✓ Server is running")
    print(f"✓ Login page loads ({len(html)} bytes)")
except Exception as e:
    print(f"✗ Error: {e}")

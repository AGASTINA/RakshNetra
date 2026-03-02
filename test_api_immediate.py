import urllib.request
import json
import time

time.sleep(2)  # Give server time to start

try:
    with urllib.request.urlopen('http://127.0.0.1:8000/api/events/') as response:
        data = json.loads(response.read())
        print("API Response:")
        print(json.dumps(data, indent=2)[:500])  # First 500 chars
except Exception as e:
    print(f"Error: {e}")

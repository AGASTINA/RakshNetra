import time
import urllib.request
time.sleep(2)
try:
    # Test dashboard
    response = urllib.request.urlopen('http://127.0.0.1:8000/', timeout=3)
    print('✓ Dashboard loads')
    
    # Test video file serving
    response2 = urllib.request.urlopen('http://127.0.0.1:8000/media/draupathi_murmur.mp4', timeout=3)
    size = response2.headers.get('Content-Length', '?')
    ctype = response2.headers.get('Content-Type', '?')
    print(f'✓ Video file accessible ({size} bytes, {ctype})')
except Exception as e:
    print(f'✗ Error: {e}')

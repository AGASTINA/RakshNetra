import urllib.request
import urllib.parse
import http.cookiejar
import json
import time

# Create a cookie jar to manage session cookies
cookie_jar = http.cookiejar.CookieJar()
opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cookie_jar))

print("Step 1: Get login page and CSRF token...")
try:
    login_page_response = opener.open('http://127.0.0.1:8000/accounts/login/')
    login_page_html = login_page_response.read().decode('utf-8')
    
    # Extract CSRF token
    import re
    csrf_match = re.search(r'csrfmiddlewaretoken["\']?\s*[=:]\s*["\']([^"\']+)["\']', login_page_html)
    if csrf_match:
        csrf_token = csrf_match.group(1)
        print(f"CSRF Token: {csrf_token[:20]}...")
    else:
        print("WARNING: Could not find CSRF token")
        csrf_token = None
except Exception as e:
    print(f"Error getting login page: {e}")
    csrf_token = None

print("\nStep 2: Login...")
try:
    login_data = urllib.parse.urlencode({
        'username': 'admin',
        'password': 'admin123',
        'csrfmiddlewaretoken': csrf_token or ''
    }).encode('utf-8')
    
    login_response = opener.open('http://127.0.0.1:8000/accounts/login/', login_data)
    print(f"Login response: {login_response.status}")
except Exception as e:
    print(f"Error logging in: {e}")

print("\nStep 3: Test API with authenticated session...")
time.sleep(1)
try:
    api_response = opener.open('http://127.0.0.1:8000/api/events/')
    data = json.loads(api_response.read())
    print(f"API Status: {api_response.status}")
    print(f"Events returned: {len(data) if isinstance(data, list) else len(data.get('results', []))}")
    if isinstance(data, list) and len(data) > 0:
        print(f"First event: {data[0].get('name', 'N/A')}")
    elif isinstance(data, dict) and 'results' in data and len(data['results']) > 0:
        print(f"First event: {data['results'][0].get('name', 'N/A')}")
except Exception as e:
    print(f"Error accessing API: {e}")

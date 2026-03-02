import django
import os
import json
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rakshnetra.settings')
django.setup()

from feeds.video import DashboardView

view = DashboardView()
view.request = type('Request', (), {})()
ctx = view.get_context_data()
print('Template context prepared:')
print(f'  - cameras_json: {len(ctx["cameras_json"])} chars')
print(f'  - events_json: {len(ctx["events_json"])} chars')
print(f'  - cameras_json valid: {json.loads(ctx["cameras_json"]) is not None}')
print(f'  - events_json valid: {json.loads(ctx["events_json"]) is not None}')
print('\nFirst camera:', json.loads(ctx['cameras_json'])[0] if json.loads(ctx['cameras_json']) else 'None')
print('First event:', json.loads(ctx['events_json'])[0] if json.loads(ctx['events_json']) else 'None')

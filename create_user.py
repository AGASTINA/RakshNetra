#!/usr/bin/env python
import django
import os
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'rakshnetra.settings')
django.setup()

from accounts.models import User

users = User.objects.all()
print(f"Total users: {users.count()}")
for u in users:
    print(f"  - {u.username} (staff: {u.is_staff}, superuser: {u.is_superuser})")

if users.count() == 0:
    print("\nCreating test user...")
    User.objects.create_superuser('admin', 'admin@test.local', 'admin123')
    print("✓ Created superuser: admin/admin123")


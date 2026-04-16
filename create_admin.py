#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from users.models import User

# Create superuser
if not User.objects.filter(username='admin').exists():
    User.objects.create_superuser(
        username='admin',
        email='admin@cuea.edu',
        password='Admin@123',
        role='admin'
    )
    print("✅ Superuser 'admin' created successfully!")
    print("   Username: admin")
    print("   Email: admin@cuea.edu")
    print("   Password: Admin@123")
    print("   Role: Admin")
else:
    print("⚠️ Superuser 'admin' already exists!")
    user = User.objects.get(username='admin')
    user.set_password('Admin@123')
    user.is_staff = True
    user.is_superuser = True
    user.role = 'admin'
    user.save()
    print("✅ Password reset to: Admin@123")

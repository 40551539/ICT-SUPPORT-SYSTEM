#!/usr/bin/env python
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'config.settings')
django.setup()

from tickets.models import Category

# List of default categories for the help desk
default_categories = [
    {
        'name': 'Network & Internet',
        'description': 'WiFi, internet connectivity, VPN, and network issues'
    },
    {
        'name': 'Hardware',
        'description': 'Printer setup, device configuration, peripherals'
    },
    {
        'name': 'Software',
        'description': 'Application installation, updates, software issues'
    },
    {
        'name': 'Student Portal',
        'description': 'Issues accessing the student portal, password resets, account problems'
    },
    {
        'name': 'Email & Accounts',
        'description': 'Email configuration, account access, password resets'
    },
    {
        'name': 'System Access',
        'description': 'Login issues, access permissions, account lockouts'
    },
    {
        'name': 'General IT Support',
        'description': 'Other IT-related issues not covered by above categories'
    },
]

# Create categories
created_count = 0
for cat_data in default_categories:
    category, created = Category.objects.get_or_create(
        name=cat_data['name'],
        defaults={'description': cat_data['description']}
    )
    if created:
        created_count += 1
        print(f"✅ Created category: {category.name}")
    else:
        print(f"⚠️  Category already exists: {category.name}")

print(f"\n📊 Categories ready: {Category.objects.count()} total")

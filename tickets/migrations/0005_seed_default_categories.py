from django.db import migrations


DEFAULT_CATEGORIES = [
    ('Network & Internet', 'WiFi, internet connectivity, VPN, and network issues'),
    ('Hardware', 'Printer setup, device configuration, and peripheral issues'),
    ('Software', 'Application installation, updates, and software issues'),
    ('Student Portal', 'Student portal access, password, and account issues'),
    ('Email & Accounts', 'Email configuration, account access, and password resets'),
    ('System Access', 'Login issues, access permissions, and account lockouts'),
    ('General IT Support', 'Other IT-related issues'),
]


def seed_categories(apps, schema_editor):
    Category = apps.get_model('tickets', 'Category')
    for name, description in DEFAULT_CATEGORIES:
        Category.objects.get_or_create(name=name, defaults={'description': description})


class Migration(migrations.Migration):

    dependencies = [
        ('tickets', '0004_internalnote'),
    ]

    operations = [
        migrations.RunPython(seed_categories, migrations.RunPython.noop),
    ]

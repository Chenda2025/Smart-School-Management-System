from django.db import migrations
from django.contrib.auth import get_user_model

def create_superuser(apps, schema_editor):
    User = get_user_model()
    if not User.objects.filter(username='admin').exists():  # change 'admin' if different
        User.objects.create_superuser(
            username='admin',                  # ← CHANGE to your username (e.g., 'chenda' or 'sbc')
            email='admin@example.com',         # ← CHANGE to your email or ''
            password='admin12345'   # ← CHANGE to your real password
        )

class Migration(migrations.Migration):
    dependencies = [
        ('core', '0010_auto_20260109_1904'),  # ← this is correct for your project
    ]

    operations = [
        migrations.RunPython(create_superuser),
    ]
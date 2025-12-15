import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horilla.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

# Try to find admin user
admin = User.objects.filter(username='admin').first()

if not admin:
    # Try to find any superuser
    admin = User.objects.filter(is_superuser=True).first()

if not admin:
    # List all users
    print("No admin user found. Available users:")
    for user in User.objects.all()[:10]:
        print(f"  - Username: {user.username}, Is Staff: {user.is_staff}, Is Superuser: {user.is_superuser}")
else:
    print(f"Found admin user: {admin.username}")
    admin.set_password('admin123')
    admin.save()
    print(f"Password for '{admin.username}' has been reset to: admin123")
    print(f"You can now login with:")
    print(f"  Username: {admin.username}")
    print(f"  Password: admin123")

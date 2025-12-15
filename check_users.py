import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horilla.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

print("=" * 60)
print("ALL USERS IN DATABASE:")
print("=" * 60)

users = User.objects.all()
print(f"\nTotal users: {users.count()}\n")

for user in users:
    print(f"Username: {user.username}")
    print(f"  Email: {user.email}")
    print(f"  Is Active: {user.is_active}")
    print(f"  Is Staff: {user.is_staff}")
    print(f"  Is Superuser: {user.is_superuser}")
    print(f"  Has usable password: {user.has_usable_password()}")
    print("-" * 60)

# Try to authenticate with admin/admin123
from django.contrib.auth import authenticate

print("\n" + "=" * 60)
print("TESTING AUTHENTICATION:")
print("=" * 60)

test_user = authenticate(username='admin', password='admin123')
if test_user:
    print(f"✓ Authentication SUCCESSFUL for 'admin' with password 'admin123'")
    print(f"  User: {test_user.username}")
    print(f"  Is Active: {test_user.is_active}")
else:
    print("✗ Authentication FAILED for 'admin' with password 'admin123'")
    
    # Try other common passwords
    for pwd in ['admin', 'password', '123456', 'Admin@123']:
        test = authenticate(username='admin', password=pwd)
        if test:
            print(f"✓ Found working password: '{pwd}'")
            break

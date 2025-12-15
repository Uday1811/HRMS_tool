import os
import django
import sys

# Add the project root to the python path
sys.path.append(os.getcwd())

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "horilla.settings")
django.setup()

from django.contrib.auth.models import User, Permission
from base.models import Company
from employee.models import Employee, EmployeeWorkInformation
from django.db import transaction

def fix_admins():
    admins = [
        {
            "username": "admin.bluebix",
            "email": "admin@bluebix.com",
            "password": "password123",
            "company_name": "Bluebix",
            "first_name": "Admin",
            "last_name": "Bluebix"
        },
        {
            "username": "admin.softstandard",
            "email": "admin@softstandard.com",
            "password": "password123",
            "company_name": "Softstandard",
            "first_name": "Admin",
            "last_name": "Softstandard"
        }
    ]

    for admin in admins:
        print(f"Processing {admin['username']}...")
        try:
            with transaction.atomic():
                # 1. Company
                company, created = Company.objects.get_or_create(
                    company=admin['company_name'],
                    defaults={"email": admin['email']}
                )
                if created:
                    print(f"Created company: {company.company}")
                else:
                    print(f"Found company: {company.company}")

                # 2. User
                user, created = User.objects.get_or_create(username=admin['username'])
                user.set_password(admin['password'])
                user.email = admin['email']
                user.first_name = admin['first_name']
                user.last_name = admin['last_name']
                user.is_staff = True
                user.is_superuser = False
                user.is_active = True
                user.save()
                print(f"Updated user: {user.username}")

                # 3. Permissions
                # Give all permissions except Company (to prevent seeing other companies)
                # Also ensure they have 'view_employee' etc.
                from django.contrib.contenttypes.models import ContentType
                company_ct = ContentType.objects.get_for_model(Company)
                all_permissions = Permission.objects.exclude(content_type=company_ct)
                user.user_permissions.set(all_permissions)
                user.save()
                
                # 4. Employee
                employee = None
                try:
                    employee = Employee.objects.get(employee_user_id=user)
                except Employee.DoesNotExist:
                    # Try to find by email
                    try:
                        employee = Employee.objects.get(email=admin['email'])
                        employee.employee_user_id = user
                        employee.save()
                        print(f"Linked existing employee (by email) to user: {employee}")
                    except Employee.DoesNotExist:
                        employee = Employee.objects.create(
                            employee_user_id=user,
                            email=admin['email'],
                            employee_first_name=admin['first_name'],
                            employee_last_name=admin['last_name']
                        )
                        print(f"Created new employee: {employee}")

                employee.employee_first_name = admin['first_name']
                employee.employee_last_name = admin['last_name']
                employee.is_active = True
                employee.save()
                print(f"Updated employee: {employee}")

                # 5. Work Info (Link to Company)
                work_info, created = EmployeeWorkInformation.objects.get_or_create(employee_id=employee)
                work_info.company_id = company
                work_info.save()
                print(f"Linked employee to company: {company.company}")

        except Exception as e:
            print(f"Failed to process {admin['username']}: {e}")

if __name__ == "__main__":
    fix_admins()

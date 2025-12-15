import os
import django
from django.utils import timezone

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "horilla.settings")
django.setup()

from base.models import Company
from django.contrib.auth.models import User, Group, Permission
from employee.models import Employee, EmployeeWorkInformation

def setup_company_admins():
    print("Setting up Company Admins...")

    # Define the admins to create
    admin_data = [
        {
            "username": "admin.petabytz",
            "email": "admin@petabytz.com",
            # "password": "password123", # Will set below
            "company_domain": "petabytz.com",
            "first_name": "Admin",
            "last_name": "Petabytz"
        },
        {
            "username": "admin.bluebix",
            "email": "admin@bluebix.com",
            "company_domain": "bluebix.com",
            "first_name": "Admin",
            "last_name": "Bluebix"
        },
        {
            "username": "admin.softstandard",
            "email": "admin@softstandard.com",
            "company_domain": "softstandard.com",
            "first_name": "Admin",
            "last_name": "Softstandard"
        }
    ]

    # Get "Manager" or "Admin" group permissions
    # We want these users to have almost all permissions EXCEPT superuser status
    # Let's collect all permissions
    all_permissions = Permission.objects.all()

    for data in admin_data:
        company = Company.get_company_by_email(data["email"])
        if not company:
            print(f"Error: Company not found for domain {data['company_domain']}")
            continue

        # Create or Get User
        user, created = User.objects.get_or_create(username=data["username"])
        if created:
            user.set_password("password123")
        user.email = data["email"]
        user.first_name = data["first_name"]
        user.last_name = data["last_name"]
        user.is_staff = True 
        user.is_superuser = False 
        user.save()

        user.save()

        # Assign permissions (Exclude Company model permissions to prevent switching/listing all companies)
        from django.contrib.contenttypes.models import ContentType
        company_ct = ContentType.objects.get_for_model(Company)
        company_perms = Permission.objects.filter(content_type=company_ct)
        
        filtered_perms = [p for p in all_permissions if p not in company_perms]
        user.user_permissions.set(filtered_perms)
        user.save()

        # Handle Employee Creation/Linking safely
        employee = None
        # 1. Try to find by email
        try:
            employee = Employee.objects.get(email=data["email"])
            print(f"Found existing employee by email: {employee}")
            # Ensure it's linked to our user
            if employee.employee_user_id != user:
                employee.employee_user_id = user
                employee.save()
        except Employee.DoesNotExist:
            # 2. Try to find by user
            try:
                employee = Employee.objects.get(employee_user_id=user)
                print(f"Found existing employee by user: {employee}")
                # Update email
                employee.email = data["email"]
                employee.save()
            except Employee.DoesNotExist:
                # 3. Create new
                print("Creating new employee")
                employee = Employee.objects.create(
                    employee_user_id=user,
                    email=data["email"],
                    employee_first_name=data["first_name"],
                    employee_last_name=data["last_name"],
                    phone="0000000000" # Dummy phone
                )

        # Update details
        employee.employee_first_name = data["first_name"]
        employee.employee_last_name = data["last_name"]
        employee.save()

        # Link to Company
        work_info, work_created = EmployeeWorkInformation.objects.get_or_create(employee_id=employee)
        work_info.company_id = company
        work_info.save()

        print(f"Successfully setup admin: {data['username']} for {company.company}")

if __name__ == "__main__":
    setup_company_admins()

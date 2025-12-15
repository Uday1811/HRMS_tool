
import os
import django
from django.conf import settings

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horilla.settings')
django.setup()

from django.contrib.auth import get_user_model
from employee.models import Employee
from base.models import Company

User = get_user_model()

def create_company_if_not_exists():
    if not Company.objects.exists():
        print("Creating default company...")
        Company.objects.create(company="Petabytz", hq=True)
    else:
        print("Company exists.")

def create_employee(badge_id, first_name, email, phone):
    if Employee.objects.filter(badge_id=badge_id).exists():
        print(f"Employee {badge_id} already exists.")
        return

    print(f"Creating Employee {badge_id}...")
    try:
        emp = Employee(
            badge_id=badge_id,
            employee_first_name=first_name,
            email=email,
            phone=phone
        )
        emp.save()
        print(f"Created Employee {badge_id}. User created with username '{email}' and password '{phone}'.")
        
        # Verify user linkage
        if emp.employee_user_id:
             print(f"Linked User: {emp.employee_user_id.username}")
        else:
             print("Warning: No user linked!")

    except Exception as e:
        print(f"Error creating {badge_id}: {e}")

if __name__ == "__main__":
    create_company_if_not_exists()
    create_employee("PEP0002", "Pep Two", "pep0002@example.com", "password123")
    create_employee("PEP0003", "Pep Three", "pep0003@example.com", "password123")
    create_employee("3", "Number Three", "number3@example.com", "password123")

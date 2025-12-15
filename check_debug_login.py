import os
import django
import sys

# Add the project root to the python path
sys.path.append(os.getcwd())

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "horilla.settings")
django.setup()

from django.contrib.auth.models import User
from base.models import Company
from employee.models import Employee, EmployeeWorkInformation

def check_users():
    usernames = ["admin.petabytz", "admin.bluebix", "admin.softstandard"]
    
    for username in usernames:
        print(f"--- Checking {username} ---")
        user = User.objects.filter(username=username).first()
        if not user:
            print(f"User {username} NOT FOUND in User model.")
            continue
        
        print(f"User found: ID={user.id}, Active={user.is_active}, Superuser={user.is_superuser}")
        if not user.check_password("password123"):
            print("Password check FAILED for 'password123'")
        else:
            print("Password check PASSED")
            
        try:
            employee = user.employee_get
            print(f"Employee linked: {employee} (ID={employee.id})")
            
            try:
                work_info = employee.employee_work_info
                company = work_info.company_id
                print(f"Company linked: {company} (ID={company.id})")
            except Exception as e:
                print(f"Work Info/Company error: {e}")
                
        except Exception as e:
            print(f"Employee link error: {e}")
            
    # Also list all companies
    print("\n--- Companies ---")
    for c in Company.objects.all():
        print(f"Company: {c.company} (ID={c.id}, Domain={c.email if hasattr(c, 'email') else 'N/A'})")

if __name__ == "__main__":
    check_users()

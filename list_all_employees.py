import os
import django
from django.conf import settings

# Setup Django environment
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'io.settings') # Assuming 'io' is the project name based on file structure or similar, but let's check manage.py usually sets this. 
# Actually, manage.py usually does this. Since I'm running via `python manage.py shell`, I don't need to setup manually if I use that method.
# But if the user wants "the file", I should write a standalone script or just a script to be run with shell.

from employee.models import Employee

def list_employees():
    print("--- Fetching All Employees ---")
    try:
        # Try custom manager then default
        try:
            employees = Employee.objects.entire()
        except AttributeError:
            employees = Employee.objects.all()
            
        count = employees.count()
        print(f"Total Employees Found: {count}")
        print("-" * 50)
        print(f"{'ID':<5} | {'Badge ID':<10} | {'Name':<25} | {'Email':<30} | {'Active'}")
        print("-" * 50)
        
        for emp in employees:
            full_name = f"{emp.employee_first_name} {emp.employee_last_name}"
            print(f"{emp.id:<5} | {str(emp.badge_id):<10} | {full_name:<25} | {emp.email:<30} | {emp.is_active}")
            
    except Exception as e:
        print(f"Error occurred: {e}")

if __name__ == "__main__":
    list_employees()

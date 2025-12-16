
import sys
from employee.models import Employee

try:
    with open('employee_list_output.txt', 'w') as f:
        f.write("--- Employee Database Dump ---\n")
        try:
            employees = Employee.objects.entire()
        except:
            employees = Employee.objects.all()
            
        f.write(f"Total Count: {employees.count()}\n\n")
        f.write(f"{'ID':<5} | {'Badge ID':<10} | {'Name':<30} | {'Email':<30}\n")
        f.write("-" * 80 + "\n")
        
        for e in employees:
            full_name = f"{e.employee_first_name} {e.employee_last_name}"
            f.write(f"{e.id:<5} | {str(e.badge_id):<10} | {full_name:<30} | {e.email:<30}\n")
            
    print("Successfully wrote to employee_list_output.txt")
except Exception as e:
    print(f"Error: {e}")

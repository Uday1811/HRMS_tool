
import sys
from employee.models import Employee

# NON-INTERACTIVE SCRIPT - JUST LISTS AND DELETES IF ARG PROVIDED

def print_table(headers, data):
    widths = [len(h) for h in headers]
    for row in data:
        for i, item in enumerate(row):
            widths[i] = max(widths[i], len(str(item)))
    
    fmt = " | ".join([f"{{:<{w}}}" for w in widths])
    print("-" * (sum(widths) + 3 * (len(headers) - 1)))
    print(fmt.format(*headers))
    print("-" * (sum(widths) + 3 * (len(headers) - 1)))
    for row in data:
        print(fmt.format(*[str(x) for x in row]))
    print("-" * (sum(widths) + 3 * (len(headers) - 1)))

def list_employees():
    try:
        employees = Employee.objects.entire().order_by('id')
    except:
        employees = Employee.objects.all().order_by('id')

    data = []
    for e in employees:
        full_name = f"{e.employee_first_name} {e.employee_last_name}"
        data.append([e.id, e.badge_id, full_name, e.email])
    
    print("\nCURRENT EMPLOYEE LIST:")
    print_table(["ID", "Badge ID", "Name", "Email"], data)

def delete_employee(emp_id):
    try:
        emp = Employee.objects.get(id=emp_id)
        name = f"{emp.employee_first_name} {emp.employee_last_name}"
        emp.delete()
        print(f"\nSUCCESS: Deleted Employee ID {emp_id} ({name})")
    except Employee.DoesNotExist:
        print(f"\nERROR: Employee ID {emp_id} not found.")
    except Exception as e:
        print(f"\nERROR: Could not delete. {e}")

# Run Logic
list_employees()

# TO DELETE: Change this variable manually or run a specific command
# delete_id = 16 
# delete_employee(delete_id)

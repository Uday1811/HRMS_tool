
import os
import django
import sys

# Setup Django environment manually
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horilla.settings')
django.setup()
print("Django setup complete.", flush=True)

from employee.models import Employee

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
    print("\nConnecting to database...")
    try:
        # Try to use the custom manager if it exists, else default
        if hasattr(Employee.objects, 'entire'):
            employees = Employee.objects.entire().order_by('id')
        else:
            employees = Employee.objects.all().order_by('id')
            
        count = employees.count()
        print(f"Total Employees: {count}")

        data = []
        for e in employees:
            full_name = f"{e.employee_first_name} {e.employee_last_name}"
            data.append([e.id, e.badge_id, full_name, e.email])
        
        print("\n--- EMPLOYEE LIST ---")
        print_table(["ID", "Badge ID", "Name", "Email"], data)
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    if len(sys.argv) > 1 and sys.argv[1] == 'delete':
        try:
            emp_id = sys.argv[2]
            print(f"Attempting to delete Employee ID: {emp_id}...")
            
            # Find the employee
            emp = Employee.objects.get(id=emp_id)
            
            # Check for generic related objects that might be protected (Contract is the one mentioned in error)
            # We import Contract dynamically or check related manager
            try:
                from payroll.models.models import Contract
                contracts = Contract.objects.filter(employee_id=emp)
                count = contracts.count()
                if count > 0:
                    print(f"Found {count} related Contracts. Deleting them first...")
                    contracts.delete()
            except ImportError:
                 print("Payroll module not found or Contract model not available. Skipping.")
            except Exception as e:
                print(f"Warning checking contracts: {e}")

            # Check for Attendance related objects
            try:
                from attendance.models import Attendance, AttendanceActivity, AttendanceOverTime
                
                # Delete AttendanceActivity
                activities = AttendanceActivity.objects.filter(employee_id=emp)
                if activities.exists():
                    count = activities.count()
                    print(f"Found {count} Attendance Activities. Deleting...")
                    activities.delete()
                    
                # Delete AttendanceOverTime
                ot = AttendanceOverTime.objects.filter(employee_id=emp)
                if ot.exists():
                    count = ot.count()
                    print(f"Found {count} Attendance Overtime records. Deleting...")
                    ot.delete()

                # Delete Attendance
                atts = Attendance.objects.filter(employee_id=emp)
                if atts.exists():
                    count = atts.count()
                    print(f"Found {count} Attendance records. Deleting...")
                    atts.delete()
                    
            except ImportError:
                print("Attendance module not found. Skipping.")
            except Exception as e:
                print(f"Warning checking attendance: {e}")

            # Now try deleting employee
            emp.delete()
            print("SUCCESS: Deleted.")
            
        except Exception as e:
            print(f"ERROR: {e}")
            
    list_employees()

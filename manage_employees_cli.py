import sys
from employee.models import Employee

def print_table(headers, data):
    # Calculate column widths
    widths = [len(h) for h in headers]
    for row in data:
        for i, item in enumerate(row):
            widths[i] = max(widths[i], len(str(item)))
    
    # Create format string
    fmt = " | ".join([f"{{:<{w}}}" for w in widths])
    
    # Print header
    print("-" * (sum(widths) + 3 * (len(headers) - 1)))
    print(fmt.format(*headers))
    print("-" * (sum(widths) + 3 * (len(headers) - 1)))
    
    # Print rows
    for row in data:
        print(fmt.format(*[str(x) for x in row]))
    print("-" * (sum(widths) + 3 * (len(headers) - 1)))

def get_employees():
    try:
        return Employee.objects.entire()
    except:
        return Employee.objects.all()

def main():
    while True:
        employees = get_employees().order_by('id')
        data = []
        for e in employees:
            full_name = f"{e.employee_first_name} {e.employee_last_name}"
            data.append([e.id, e.badge_id, full_name, e.email, "Yes" if e.is_active else "No"])
            
        print("\n--- EMPLOYEE DATABASE ---")
        print_table(["ID", "Badge ID", "Name", "Email", "Active"], data)
        print(f"Total Records: {len(data)}")
        
        print("\nCOMMANDS:")
        print("  delete <ID>   : Delete an employee by ID")
        print("  refresh       : Refresh the list")
        print("  quit          : Exit")
        
        try:
            cmd_input = input("\nSQL> ").strip().split()
        except EOFError:
            break
            
        if not cmd_input:
            continue
            
        cmd = cmd_input[0].lower()
        
        if cmd == 'quit' or cmd == 'exit':
            break
        elif cmd == 'refresh':
            continue
        elif cmd == 'delete':
            if len(cmd_input) < 2:
                print("Error: Please provide an ID. Usage: delete <ID>")
                continue
            
            try:
                emp_id = int(cmd_input[1])
                try:
                    emp = Employee.objects.get(id=emp_id)
                    confirm = input(f"Are you sure you want to delete {emp.employee_first_name} {emp.employee_last_name} (ID: {emp.id})? (y/n): ")
                    if confirm.lower() == 'y':
                        emp.delete()
                        print(f"SUCCESS: Employee {emp_id} deleted.")
                    else:
                        print("Cancelled.")
                except Employee.DoesNotExist:
                    print(f"Error: Employee with ID {emp_id} not found.")
            except ValueError:
                print("Error: Invalid ID format.")
        else:
            print("Unknown command.")

if __name__ == "__main__":
    main()

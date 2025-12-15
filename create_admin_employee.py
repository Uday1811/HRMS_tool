import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'horilla.settings')
django.setup()

from django.contrib.auth import get_user_model
from employee.models import Employee, EmployeeWorkInformation
from base.models import Company, Department, JobPosition, EmployeeType
from django.db import connection

User = get_user_model()

print("=" * 60)
print("SETTING UP ADMIN LOGIN")
print("=" * 60)

# Get admin user
admin = User.objects.get(username='admin')
print(f"\n1. Found admin user: {admin.username}")

# Check if admin has an employee profile
has_employee = False
try:
    employee = admin.employee_get
    print(f"2. ✓ Admin already has an employee profile")
    print(f"   Is Active: {employee.is_active}")
    if not employee.is_active:
        employee.is_active = True
        employee.save()
        print(f"   ✓ Activated employee profile")
    has_employee = True
except Exception as e:
    print(f"2. ✗ Admin does not have an employee profile")

if not has_employee:
    # Get or create required records
    company = Company.objects.first()
    if not company:
        print("\n✗ ERROR: No company found in database!")
        exit(1)
    print(f"\n3. Using company: {company.company}")
    
    department = Department.objects.first()
    if not department:
        print("\n✗ ERROR: No department found in database!")
        exit(1)
    print(f"4. Using department: {department.department}")
    
    # Get or create Employee Type using raw SQL to bypass clean()
    employee_type = EmployeeType.objects.filter(employee_type='Full-Time').first()
    if not employee_type:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO base_employeetype (employee_type) VALUES (?)",
                ['Full-Time']
            )
        employee_type = EmployeeType.objects.get(employee_type='Full-Time')
        print(f"5. Created employee type: {employee_type.employee_type}")
    else:
        print(f"5. Using employee type: {employee_type.employee_type}")
    
    # Get or create Job Position
    job_position = JobPosition.objects.filter(department_id=department).first()
    if not job_position:
        with connection.cursor() as cursor:
            cursor.execute(
                "INSERT INTO base_jobposition (job_position, department_id_id, is_active) VALUES (?, ?, ?)",
                ['Administrator', department.id, True]
            )
        job_position = JobPosition.objects.get(job_position='Administrator', department_id=department)
        if company:
            job_position.company_id.add(company)
        print(f"6. Created job position: {job_position.job_position}")
    else:
        print(f"6. Using job position: {job_position.job_position}")
    
    # Create employee profile
    print(f"\n7. Creating employee profile...")
    employee = Employee.objects.create(
        employee_user_id=admin,
        employee_first_name='Admin',
        employee_last_name='User',
        email=admin.email,
        phone='0000000000',
        is_active=True
    )
    print(f"   ✓ Created employee: {employee.employee_first_name} {employee.employee_last_name}")
    
    # Create work information
    print(f"8. Creating work information...")
    work_info = EmployeeWorkInformation.objects.create(
        employee_id=employee,
        email=admin.email,
        company_id=company,
        department_id=department,
        job_position_id=job_position,
        employee_type_id=employee_type,
        reporting_manager_id=None
    )
    print(f"   ✓ Created work information")
    
    print("\n" + "=" * 60)
    print("✓ ADMIN EMPLOYEE PROFILE CREATED SUCCESSFULLY!")
    print("=" * 60)

print(f"\n{'='*60}")
print(f"LOGIN CREDENTIALS:")
print(f"{'='*60}")
print(f"  Username: admin")
print(f"  Password: admin123")
print(f"{'='*60}")
print(f"\nPlease login at: http://localhost:8000/login/")

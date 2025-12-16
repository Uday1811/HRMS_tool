from django.core.management.base import BaseCommand
from django.utils import timezone
from employee.models import Employee, EmployeeLeaveBalance
import logging

logger = logging.getLogger(__name__)

class Command(BaseCommand):
    help = 'Accrues monthly leave (1 CL, 1 SL) for all active employees'

    def handle(self, *args, **options):
        self.stdout.write("Starting monthly leave accrual...")
        
        employees = Employee.objects.filter(is_active=True)
        current_year = timezone.now().year
        count = 0

        for employee in employees:
            try:
                # Accrue CL
                cl_bal, _ = EmployeeLeaveBalance.objects.get_or_create(
                    employee=employee,
                    leave_type='cl',
                    year=current_year,
                    defaults={'available_days': 0, 'total_accrued': 0, 'used_days': 0}
                )
                cl_bal.available_days += 1
                cl_bal.total_accrued += 1
                cl_bal.save()

                # Accrue SL
                sl_bal, _ = EmployeeLeaveBalance.objects.get_or_create(
                    employee=employee,
                    leave_type='sl',
                    year=current_year,
                    defaults={'available_days': 0, 'total_accrued': 0, 'used_days': 0}
                )
                sl_bal.available_days += 1
                sl_bal.total_accrued += 1
                sl_bal.save()
                
                count += 1
            except Exception as e:
                self.stderr.write(f"Error processing employee {employee}: {str(e)}")

        self.stdout.write(self.style.SUCCESS(f'Successfully accrued leaves for {count} employees.'))
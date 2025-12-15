from django.core.management.base import BaseCommand
from django.utils import timezone
from employee.models import Employee, EmployeeLeaveBalance
from django.db import transaction

class Command(BaseCommand):
    help = 'Accrues monthly leaves (1 EL, 1 SL) to all active employees'

    def handle(self, *args, **options):
        today = timezone.now().date()
        year = today.year
        month = today.month
        
        self.stdout.write(f"Starting leave accrual for Month: {month}, Year: {year}")
        
        employees = Employee.objects.all()
        count = 0
        
        with transaction.atomic():
            for emp in employees:
                # Add 1 EL
                el_balance, created = EmployeeLeaveBalance.objects.get_or_create(
                    employee=emp,
                    leave_type='el',
                    year=year,
                    defaults={'available_days': 0, 'total_accrued': 0}
                )
                el_balance.add_accrual(1.0)
                
                # Add 1 SL
                sl_balance, created = EmployeeLeaveBalance.objects.get_or_create(
                    employee=emp,
                    leave_type='sl',
                    year=year,
                    defaults={'available_days': 0, 'total_accrued': 0}
                )
                sl_balance.add_accrual(1.0)
                
                # Ensure CL exists (0 accrual, usually yearly, but ensuring existence)
                EmployeeLeaveBalance.objects.get_or_create(
                    employee=emp,
                    leave_type='cl',
                    year=year,
                    defaults={'available_days': 0, 'total_accrued': 0}
                )
                
                count += 1
                
        self.stdout.write(self.style.SUCCESS(f"Successfully accrued leaves for {count} employees"))

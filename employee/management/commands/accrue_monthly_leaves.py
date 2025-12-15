"""
Management command to accrue monthly leaves for all employees
This command should be run monthly via cron job
"""

from django.core.management.base import BaseCommand
from django.apps import apps
from django.utils import timezone
from datetime import date, datetime
from employee.models import Employee


class Command(BaseCommand):
    help = 'Accrue monthly leaves for all active employees'

    def add_arguments(self, parser):
        parser.add_argument(
            '--month',
            type=int,
            help='Month to accrue leaves for (1-12)',
            default=None
        )
        parser.add_argument(
            '--year',
            type=int,
            help='Year to accrue leaves for',
            default=None
        )
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Show what would be done without making changes',
        )

    def handle(self, *args, **options):
        if not apps.is_installed('leave'):
            self.stdout.write(
                self.style.ERROR('Leave app is not installed')
            )
            return

        from leave.models import LeaveType, AvailableLeave

        # Get current month/year or use provided values
        current_date = date.today()
        month = options['month'] or current_date.month
        year = options['year'] or current_date.year
        dry_run = options['dry_run']

        self.stdout.write(f'Processing leave accrual for {month}/{year}')

        # Get or create leave types
        paid_leave_type, created = LeaveType.objects.get_or_create(
            name='Paid Leave',
            defaults={
                'color': '#007bff',
                'limit_leave': True,
                'total_days': 12,  # 12 days per year
                'reset': True,
                'reset_based': 'yearly',
                'reset_month': '1',
                'reset_day': '1'
            }
        )
        if created:
            self.stdout.write(f'Created Paid Leave type')

        sick_leave_type, created = LeaveType.objects.get_or_create(
            name='Sick Leave',
            defaults={
                'color': '#28a745',
                'limit_leave': True,
                'total_days': 12,  # 12 days per year
                'reset': True,
                'reset_based': 'yearly',
                'reset_month': '1',
                'reset_day': '1'
            }
        )
        if created:
            self.stdout.write(f'Created Sick Leave type')

        # Get all active employees
        active_employees = Employee.objects.filter(
            employee_work_info__isnull=False,
            is_active=True
        )

        accrued_count = 0
        for employee in active_employees:
            try:
                # Check if employee joined before this month
                work_info = getattr(employee, 'employee_work_info', None)
                if not work_info or not work_info.date_joining:
                    continue

                join_date = work_info.date_joining
                accrual_date = date(year, month, 1)
                
                if join_date > accrual_date:
                    continue  # Employee not yet joined

                # Accrue Paid Leave
                paid_leave, created = AvailableLeave.objects.get_or_create(
                    employee_id=employee,
                    leave_type_id=paid_leave_type,
                    defaults={
                        'available_days': 0,
                        'total_leave_days': 0,
                        'carryforward_days': 0
                    }
                )

                if not dry_run:
                    # Add 1 day to available and total
                    paid_leave.available_days += 1
                    paid_leave.total_leave_days += 1
                    paid_leave.save()

                # Accrue Sick Leave
                sick_leave, created = AvailableLeave.objects.get_or_create(
                    employee_id=employee,
                    leave_type_id=sick_leave_type,
                    defaults={
                        'available_days': 0,
                        'total_leave_days': 0,
                        'carryforward_days': 0
                    }
                )

                if not dry_run:
                    # Add 1 day to available and total
                    sick_leave.available_days += 1
                    sick_leave.total_leave_days += 1
                    sick_leave.save()

                accrued_count += 1
                
                if dry_run:
                    self.stdout.write(f'Would accrue leaves for: {employee.employee_first_name} {employee.employee_last_name}')
                else:
                    self.stdout.write(f'Accrued leaves for: {employee.employee_first_name} {employee.employee_last_name}')

            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'Error processing {employee}: {str(e)}')
                )

        if dry_run:
            self.stdout.write(
                self.style.SUCCESS(f'Dry run complete. Would process {accrued_count} employees')
            )
        else:
            self.stdout.write(
                self.style.SUCCESS(f'Successfully accrued leaves for {accrued_count} employees')
            )
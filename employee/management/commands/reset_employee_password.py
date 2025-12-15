"""
Management command to reset employee passwords
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from employee.models import Employee
from employee.utils import generate_employee_password, send_welcome_email


class Command(BaseCommand):
    help = 'Reset password for an employee and optionally send email'

    def add_arguments(self, parser):
        parser.add_argument(
            '--badge-id',
            type=str,
            help='Employee badge ID',
        )
        parser.add_argument(
            '--email',
            type=str,
            help='Employee email address',
        )
        parser.add_argument(
            '--username',
            type=str,
            help='Employee username',
        )
        parser.add_argument(
            '--password',
            type=str,
            help='New password (if not provided, will generate one)',
        )
        parser.add_argument(
            '--send-email',
            action='store_true',
            help='Send new credentials via email',
        )

    def handle(self, *args, **options):
        # Find employee
        employee = None
        
        if options['badge_id']:
            try:
                employee = Employee.objects.get(badge_id=options['badge_id'])
            except Employee.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Employee with badge ID {options["badge_id"]} not found')
                )
                return
        elif options['email']:
            try:
                employee = Employee.objects.get(email=options['email'])
            except Employee.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'Employee with email {options["email"]} not found')
                )
                return
        elif options['username']:
            try:
                user = User.objects.get(username=options['username'])
                employee = user.employee_get
            except (User.DoesNotExist, AttributeError):
                self.stdout.write(
                    self.style.ERROR(f'Employee with username {options["username"]} not found')
                )
                return
        else:
            self.stdout.write(
                self.style.ERROR('Please provide --badge-id, --email, or --username')
            )
            return

        if not employee.employee_user_id:
            self.stdout.write(
                self.style.ERROR('Employee does not have a user account')
            )
            return

        # Generate or use provided password
        new_password = options['password'] or generate_employee_password(employee)
        
        # Reset password
        user = employee.employee_user_id
        user.set_password(new_password)
        user.save()
        
        # Display credentials
        self.stdout.write(
            self.style.SUCCESS(f'Password reset successfully for {employee.employee_first_name} {employee.employee_last_name}')
        )
        self.stdout.write(f'Username: {user.username}')
        self.stdout.write(f'Employee ID: {employee.badge_id}')
        self.stdout.write(f'Email: {employee.email}')
        self.stdout.write(f'New Password: {new_password}')
        
        # Send email if requested
        if options['send_email'] and employee.email:
            if send_welcome_email(employee, user.username, new_password):
                self.stdout.write(
                    self.style.SUCCESS('Credentials sent via email successfully')
                )
            else:
                self.stdout.write(
                    self.style.WARNING('Failed to send email')
                )
        elif options['send_email']:
            self.stdout.write(
                self.style.WARNING('No email address available for this employee')
            )
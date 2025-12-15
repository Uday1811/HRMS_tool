"""
Management command to set up multi-tenant companies and test data
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from base.models import Company, Holidays
from employee.models import Employee, EmployeeWorkInformation
from datetime import date


class Command(BaseCommand):
    help = 'Set up multi-tenant companies (Petabytz, Bluebix, Softstandard) with test data'

    def add_arguments(self, parser):
        parser.add_argument(
            '--create-test-users',
            action='store_true',
            help='Create test users for each company',
        )

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Setting up multi-tenant companies...'))
        
        # Create or update companies
        self.setup_companies()
        
        # Create sample holidays
        self.setup_holidays()
        
        # Create test users if requested
        if options['create_test_users']:
            self.create_test_users()
        
        self.stdout.write(self.style.SUCCESS('Multi-tenant setup complete!'))

    def setup_companies(self):
        """Set up the three companies with multi-tenant configuration"""
        
        # Petabytz - India-based company
        petabytz, created = Company.objects.get_or_create(
            company='Petabytz',
            defaults={
                'address': 'Petabytz Technologies, India',
                'country': 'India',
                'state': 'Karnataka',
                'city': 'Bangalore',
                'zip': '560001',
                'email_domain': 'petabytz.com',
                'timezone': 'Asia/Kolkata',
                'country_code': 'IN',
                'is_multi_location': False,
                'hq': True,
            }
        )
        if not created:
            petabytz.email_domain = 'petabytz.com'
            petabytz.timezone = 'Asia/Kolkata'
            petabytz.country_code = 'IN'
            petabytz.is_multi_location = False
            petabytz.save()
        
        self.stdout.write(f"  {'✓ Created' if created else '✓ Updated'} Petabytz company")
        
        # Bluebix - US-based company
        bluebix, created = Company.objects.get_or_create(
            company='Bluebix',
            defaults={
                'address': 'Bluebix Inc., United States',
                'country': 'United States',
                'state': 'New York',
                'city': 'New York',
                'zip': '10001',
                'email_domain': 'bluebix.com',
                'timezone': 'America/New_York',
                'country_code': 'US',
                'is_multi_location': False,
                'hq': False,
            }
        )
        if not created:
            bluebix.email_domain = 'bluebix.com'
            bluebix.timezone = 'America/New_York'
            bluebix.country_code = 'US'
            bluebix.is_multi_location = False
            bluebix.save()
        
        self.stdout.write(f"  {'✓ Created' if created else '✓ Updated'} Bluebix company")
        
        # Softstandard - Multi-location company (India & Dhaka)
        softstandard, created = Company.objects.get_or_create(
            company='Softstandard',
            defaults={
                'address': 'Softstandard Solutions, India & Bangladesh',
                'country': 'India',
                'state': 'Multiple',
                'city': 'Multiple',
                'zip': '000000',
                'email_domain': 'softstandard.com',
                'timezone': 'Asia/Kolkata',
                'country_code': 'IN',
                'is_multi_location': True,
                'hq': False,
            }
        )
        if not created:
            softstandard.email_domain = 'softstandard.com'
            softstandard.timezone = 'Asia/Kolkata'
            softstandard.country_code = 'IN'
            softstandard.is_multi_location = True
            softstandard.save()
        
        self.stdout.write(f"  {'✓ Created' if created else '✓ Updated'} Softstandard company")

    def setup_holidays(self):
        """Create sample holidays for each company"""
        
        try:
            petabytz = Company.objects.get(email_domain='petabytz.com')
            bluebix = Company.objects.get(email_domain='bluebix.com')
            softstandard = Company.objects.get(email_domain='softstandard.com')
        except Company.DoesNotExist:
            self.stdout.write(self.style.ERROR('  ✗ Companies not found. Run setup_companies first.'))
            return
        
        # Petabytz holidays (Indian holidays)
        indian_holidays = [
            ('Republic Day', date(2024, 1, 26)),
            ('Independence Day', date(2024, 8, 15)),
            ('Gandhi Jayanti', date(2024, 10, 2)),
            ('Diwali', date(2024, 11, 1)),
        ]
        
        for name, holiday_date in indian_holidays:
            Holidays.objects.get_or_create(
                name=name,
                company_id=petabytz,
                start_date=holiday_date,
                defaults={
                    'end_date': holiday_date,
                    'recurring': True,
                }
            )
        
        self.stdout.write('  ✓ Created holidays for Petabytz')
        
        # Bluebix holidays (US holidays)
        us_holidays = [
            ('New Year Day', date(2024, 1, 1)),
            ('Independence Day', date(2024, 7, 4)),
            ('Thanksgiving', date(2024, 11, 28)),
            ('Christmas', date(2024, 12, 25)),
        ]
        
        for name, holiday_date in us_holidays:
            Holidays.objects.get_or_create(
                name=name,
                company_id=bluebix,
                start_date=holiday_date,
                defaults={
                    'end_date': holiday_date,
                    'recurring': True,
                }
            )
        
        self.stdout.write('  ✓ Created holidays for Bluebix')
        
        # Softstandard holidays (location-based)
        # India location holidays
        for name, holiday_date in indian_holidays:
            Holidays.objects.get_or_create(
                name=name,
                company_id=softstandard,
                location='India',
                start_date=holiday_date,
                defaults={
                    'end_date': holiday_date,
                    'recurring': True,
                }
            )
        
        # Dhaka location holidays
        dhaka_holidays = [
            ('Independence Day', date(2024, 3, 26)),
            ('Victory Day', date(2024, 12, 16)),
            ('Eid ul-Fitr', date(2024, 4, 11)),
            ('Eid ul-Adha', date(2024, 6, 17)),
        ]
        
        for name, holiday_date in dhaka_holidays:
            Holidays.objects.get_or_create(
                name=name,
                company_id=softstandard,
                location='Dhaka',
                start_date=holiday_date,
                defaults={
                    'end_date': holiday_date,
                    'recurring': True,
                }
            )
        
        self.stdout.write('  ✓ Created location-based holidays for Softstandard')

    def create_test_users(self):
        """Create test users for each company"""
        
        try:
            petabytz = Company.objects.get(email_domain='petabytz.com')
            bluebix = Company.objects.get(email_domain='bluebix.com')
            softstandard = Company.objects.get(email_domain='softstandard.com')
        except Company.DoesNotExist:
            self.stdout.write(self.style.ERROR('  ✗ Companies not found. Run setup_companies first.'))
            return
        
        # Create test users for Petabytz
        self.create_user('test.petabytz@petabytz.com', 'Test', 'Petabytz', petabytz, 'India')
        
        # Create test users for Bluebix
        self.create_user('test.bluebix@bluebix.com', 'Test', 'Bluebix', bluebix, 'New York')
        
        # Create test users for Softstandard (India location)
        self.create_user('test.india@softstandard.com', 'Test', 'India', softstandard, 'India')
        
        # Create test users for Softstandard (Dhaka location)
        self.create_user('test.dhaka@softstandard.com', 'Test', 'Dhaka', softstandard, 'Dhaka')
        
        self.stdout.write('  ✓ Created test users for all companies')

    def create_user(self, email, first_name, last_name, company, location):
        """Helper method to create a user with employee profile"""
        
        # Check if user already exists
        if User.objects.filter(email=email).exists():
            self.stdout.write(f'    - User {email} already exists, skipping')
            return
        
        # Create user
        user = User.objects.create_user(
            username=email,
            email=email,
            password='password123',
            first_name=first_name,
            last_name=last_name
        )
        
        # Create employee
        employee = Employee.objects.create(
            employee_user_id=user,
            employee_first_name=first_name,
            employee_last_name=last_name,
            email=email,
            phone='1234567890',
            badge_id=f'{company.company[:3].upper()}{Employee.objects.count():04d}'
        )
        
        # Create work information
        work_info, created = EmployeeWorkInformation.objects.get_or_create(
            employee_id=employee,
            defaults={
                'company_id': company,
                'location': location,
                'email': email,
            }
        )
        
        if not created:
            work_info.company_id = company
            work_info.location = location
            work_info.email = email
            work_info.save()
        
        self.stdout.write(f'    ✓ Created user: {email} (Badge: {employee.badge_id})')

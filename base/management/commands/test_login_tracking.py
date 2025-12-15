"""
Management command to test login tracking functionality
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from django.utils import timezone
from base.login_tracking_models import UserLoginLog


class Command(BaseCommand):
    help = 'Test login tracking functionality by creating sample login/logout records'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Username to create test logs for (default: admin)',
            default='admin'
        )
        parser.add_argument(
            '--count',
            type=int,
            help='Number of test records to create (default: 5)',
            default=5
        )

    def handle(self, *args, **options):
        username = options['username']
        count = options['count']
        
        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'User "{username}" does not exist. Please create a user first.')
            )
            return
        
        self.stdout.write(f'Creating {count} test login/logout records for user: {username}')
        
        for i in range(count):
            # Create login record
            login_log = UserLoginLog.objects.create(
                user=user,
                action=UserLoginLog.LOGIN_ACTION,
                timestamp=timezone.now() - timezone.timedelta(hours=i*2),
                ip_address=f'192.168.1.{100+i}',
                user_agent='Mozilla/5.0 (Test Browser)',
                location=f'Test Location {i+1}',
                session_key=f'test_session_{i}'
            )
            
            # Create logout record
            logout_log = UserLoginLog.objects.create(
                user=user,
                action=UserLoginLog.LOGOUT_ACTION,
                timestamp=timezone.now() - timezone.timedelta(hours=i*2-1),
                ip_address=f'192.168.1.{100+i}',
                user_agent='Mozilla/5.0 (Test Browser)',
                location=f'Test Location {i+1}',
                session_key=f'test_session_{i}'
            )
            
            self.stdout.write(f'Created login/logout pair {i+1}')
        
        total_logs = UserLoginLog.objects.filter(user=user).count()
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {count*2} test records. '
                f'Total login logs for {username}: {total_logs}'
            )
        )
        
        # Display recent logs
        recent_logs = UserLoginLog.objects.filter(user=user).order_by('-timestamp')[:5]
        self.stdout.write('\nRecent login logs:')
        for log in recent_logs:
            self.stdout.write(
                f'  {log.timestamp.strftime("%Y-%m-%d %H:%M:%S")} - '
                f'{log.get_action_display()} - {log.ip_address}'
            )
"""
Management command to view login/logout logs
"""
from django.core.management.base import BaseCommand
from django.contrib.auth.models import User
from base.login_tracking_models import UserLoginLog


class Command(BaseCommand):
    help = 'View login/logout logs'

    def add_arguments(self, parser):
        parser.add_argument(
            '--username',
            type=str,
            help='Filter by username',
        )
        parser.add_argument(
            '--action',
            type=str,
            choices=['login', 'logout'],
            help='Filter by action (login/logout)',
        )
        parser.add_argument(
            '--limit',
            type=int,
            help='Limit number of records (default: 10)',
            default=10
        )

    def handle(self, *args, **options):
        username = options.get('username')
        action = options.get('action')
        limit = options['limit']
        
        # Build queryset
        logs = UserLoginLog.objects.select_related('user').all()
        
        if username:
            try:
                user = User.objects.get(username=username)
                logs = logs.filter(user=user)
            except User.DoesNotExist:
                self.stdout.write(
                    self.style.ERROR(f'User "{username}" does not exist.')
                )
                return
        
        if action:
            logs = logs.filter(action=action)
        
        logs = logs.order_by('-timestamp')[:limit]
        
        if not logs:
            self.stdout.write(self.style.WARNING('No login logs found.'))
            return
        
        # Display header
        self.stdout.write(
            self.style.SUCCESS(
                f'{"Employee Name":<20} {"Username":<15} {"Action":<8} {"Date & Time":<20} {"IP Address":<15} {"Location":<20}'
            )
        )
        self.stdout.write('-' * 100)
        
        # Display logs
        for log in logs:
            employee_name = log.employee_name[:19] if len(log.employee_name) > 19 else log.employee_name
            username_display = log.user.username[:14] if len(log.user.username) > 14 else log.user.username
            action_display = log.get_action_display()
            timestamp_display = log.timestamp.strftime('%Y-%m-%d %H:%M:%S')
            ip_display = log.ip_address or '-'
            location_display = (log.location[:19] if log.location and len(log.location) > 19 
                              else log.location or '-')
            
            self.stdout.write(
                f'{employee_name:<20} {username_display:<15} {action_display:<8} '
                f'{timestamp_display:<20} {ip_display:<15} {location_display:<20}'
            )
        
        total_count = UserLoginLog.objects.count()
        filtered_count = UserLoginLog.objects.filter(
            **{k: v for k, v in [
                ('user__username', username),
                ('action', action)
            ] if v}
        ).count()
        
        self.stdout.write(f'\nShowing {len(logs)} of {filtered_count} records (Total: {total_count})')
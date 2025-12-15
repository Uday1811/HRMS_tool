"""
Leave management utilities for employee module
"""

from datetime import date, datetime, timedelta
from django.apps import apps
from django.db.models import Sum, Q
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
import calendar


class LeaveCalculator:
    """Utility class for leave calculations"""
    
    @staticmethod
    def calculate_working_days(start_date, end_date, exclude_weekends=True, exclude_holidays=True):
        """
        Calculate working days between two dates
        """
        if start_date > end_date:
            return 0
        
        total_days = (end_date - start_date).days + 1
        working_days = total_days
        
        if exclude_weekends:
            # Count weekends
            current_date = start_date
            weekend_days = 0
            while current_date <= end_date:
                if current_date.weekday() >= 5:  # Saturday = 5, Sunday = 6
                    weekend_days += 1
                current_date += timedelta(days=1)
            working_days -= weekend_days
        
        if exclude_holidays:
            # Count holidays (if base app is available)
            try:
                from base.models import Holidays
                holidays = Holidays.objects.filter(
                    start_date__lte=end_date,
                    end_date__gte=start_date
                )
                holiday_days = 0
                for holiday in holidays:
                    # Calculate overlap between holiday and leave period
                    overlap_start = max(holiday.start_date, start_date)
                    overlap_end = min(holiday.end_date, end_date)
                    if overlap_start <= overlap_end:
                        holiday_days += (overlap_end - overlap_start).days + 1
                working_days -= holiday_days
            except ImportError:
                pass  # Base app not available
        
        return max(0, working_days)
    
    @staticmethod
    def calculate_leave_days(start_date, end_date, duration='full_day'):
        """
        Calculate leave days considering duration (full/half day)
        """
        working_days = LeaveCalculator.calculate_working_days(start_date, end_date)
        
        if duration in ['first_half', 'second_half']:
            if start_date == end_date:
                return 0.5
            else:
                # For multi-day requests with half day on first/last day
                return working_days - 0.5
        
        return working_days
    
    @staticmethod
    def get_monthly_accrual(employee, leave_type='paid'):
        """
        Calculate monthly leave accrual for an employee
        """
        # Standard accrual rates (can be customized per company policy)
        accrual_rates = {
            'paid': 1.5,  # 1.5 days per month (18 days per year)
            'sick': 1.0,  # 1 day per month (12 days per year)
        }
        
        return accrual_rates.get(leave_type, 0)
    
    @staticmethod
    def calculate_pro_rata_accrual(join_date, leave_type='paid', current_date=None):
        """
        Calculate pro-rata leave accrual for new joiners
        """
        if not current_date:
            current_date = date.today()
        
        if join_date > current_date:
            return 0
        
        # Calculate months worked
        months_worked = (current_date.year - join_date.year) * 12 + (current_date.month - join_date.month)
        
        # Add partial month if joined mid-month
        if join_date.day <= 15:  # Joined in first half of month
            months_worked += 1
        
        monthly_accrual = LeaveCalculator.get_monthly_accrual(None, leave_type)
        return months_worked * monthly_accrual


class LeaveValidator:
    """Utility class for leave validation"""
    
    @staticmethod
    def validate_leave_dates(start_date, end_date):
        """Validate leave date range"""
        errors = []
        
        if start_date > end_date:
            errors.append(_('Start date cannot be after end date'))
        
        if start_date < date.today():
            errors.append(_('Cannot apply for past dates'))
        
        # Check for minimum advance notice (2 days)
        if (start_date - date.today()).days < 2:
            errors.append(_('Leave must be applied at least 2 days in advance'))
        
        return errors
    
    @staticmethod
    def validate_leave_balance(employee, leave_type, requested_days, year=None):
        """Validate if employee has sufficient leave balance"""
        if not year:
            year = date.today().year
        
        try:
            from employee.models.leave_models import EmployeeLeaveBalance
            balance = EmployeeLeaveBalance.objects.get(
                employee=employee,
                leave_type=leave_type,
                year=year
            )
            
            if balance.available_days < requested_days:
                return False, _(
                    'Insufficient %(leave_type)s balance. Available: %(available)s days, Requested: %(requested)s days'
                ) % {
                    'leave_type': leave_type.title(),
                    'available': balance.available_days,
                    'requested': requested_days
                }
            
            return True, None
            
        except Exception:
            return False, _('Leave balance not found')
    
    @staticmethod
    def check_overlapping_requests(employee, start_date, end_date, exclude_request_id=None):
        """Check for overlapping leave requests"""
        try:
            from employee.models.leave_models import EmployeeLeaveRequest
            
            overlapping_requests = EmployeeLeaveRequest.objects.filter(
                employee=employee,
                status__in=['pending', 'approved'],
                start_date__lte=end_date,
                end_date__gte=start_date
            )
            
            if exclude_request_id:
                overlapping_requests = overlapping_requests.exclude(id=exclude_request_id)
            
            return overlapping_requests.exists(), overlapping_requests
            
        except Exception:
            return False, None


class LeaveReportGenerator:
    """Utility class for generating leave reports"""
    
    @staticmethod
    def get_employee_leave_summary(employee, year=None):
        """Get comprehensive leave summary for an employee"""
        if not year:
            year = date.today().year
        
        try:
            from employee.models.leave_models import EmployeeLeaveBalance, EmployeeLeaveRequest
            
            # Get leave balances
            balances = EmployeeLeaveBalance.objects.filter(
                employee=employee,
                year=year
            )
            
            # Get leave requests
            requests = EmployeeLeaveRequest.objects.filter(
                employee=employee,
                start_date__year=year
            )
            
            summary = {
                'employee': employee,
                'year': year,
                'balances': {},
                'requests': {
                    'total': requests.count(),
                    'approved': requests.filter(status='approved').count(),
                    'pending': requests.filter(status='pending').count(),
                    'rejected': requests.filter(status='rejected').count(),
                    'cancelled': requests.filter(status='cancelled').count(),
                },
                'usage': {}
            }
            
            # Process balances
            for balance in balances:
                summary['balances'][balance.leave_type] = {
                    'total_accrued': balance.total_accrued,
                    'available': balance.available_days,
                    'used': balance.used_days,
                    'utilization_percentage': (balance.used_days / balance.total_accrued * 100) if balance.total_accrued > 0 else 0
                }
            
            # Process usage by month
            for month in range(1, 13):
                month_requests = requests.filter(
                    start_date__month=month,
                    status='approved'
                )
                total_days = month_requests.aggregate(
                    Sum('requested_days')
                )['requested_days__sum'] or 0
                
                summary['usage'][calendar.month_name[month]] = total_days
            
            return summary
            
        except Exception as e:
            return {'error': str(e)}
    
    @staticmethod
    def get_department_leave_report(department, year=None):
        """Get leave report for entire department"""
        if not year:
            year = date.today().year
        
        try:
            from employee.models.leave_models import EmployeeLeaveBalance, EmployeeLeaveRequest
            
            # Get all employees in department
            employees = department.employee_set.filter(is_active=True)
            
            report = {
                'department': department,
                'year': year,
                'total_employees': employees.count(),
                'leave_statistics': {},
                'top_leave_takers': [],
                'pending_approvals': 0
            }
            
            # Calculate department-wide statistics
            total_balances = EmployeeLeaveBalance.objects.filter(
                employee__in=employees,
                year=year
            )
            
            for leave_type in ['paid', 'sick']:
                type_balances = total_balances.filter(leave_type=leave_type)
                total_allocated = type_balances.aggregate(Sum('total_accrued'))['total_accrued__sum'] or 0
                total_used = type_balances.aggregate(Sum('used_days'))['used_days__sum'] or 0
                
                report['leave_statistics'][leave_type] = {
                    'total_allocated': total_allocated,
                    'total_used': total_used,
                    'utilization_percentage': (total_used / total_allocated * 100) if total_allocated > 0 else 0
                }
            
            # Get pending approvals count
            report['pending_approvals'] = EmployeeLeaveRequest.objects.filter(
                employee__in=employees,
                status='pending'
            ).count()
            
            # Get top leave takers
            top_users = EmployeeLeaveRequest.objects.filter(
                employee__in=employees,
                start_date__year=year,
                status='approved'
            ).values('employee').annotate(
                total_days=Sum('requested_days')
            ).order_by('-total_days')[:5]
            
            for user_data in top_users:
                try:
                    employee = employees.get(id=user_data['employee'])
                    report['top_leave_takers'].append({
                        'employee': employee,
                        'total_days': user_data['total_days']
                    })
                except Exception:
                    continue
            
            return report
            
        except Exception as e:
            return {'error': str(e)}


class LeaveNotificationManager:
    """Utility class for managing leave notifications"""
    
    @staticmethod
    def send_leave_application_notification(leave_request):
        """Send notification when leave is applied"""
        try:
            if apps.is_installed('notifications'):
                from notifications.signals import notify
                
                # Notify manager
                if leave_request.manager:
                    notify.send(
                        sender=leave_request.employee,
                        recipient=leave_request.manager,
                        verb='applied for leave',
                        action_object=leave_request,
                        description=f'{leave_request.employee} applied for {leave_request.get_leave_type_display()} from {leave_request.start_date} to {leave_request.end_date}'
                    )
                
                # Notify HR (if configured)
                # This can be customized based on company structure
                
        except Exception as e:
            pass  # Fail silently for notifications
    
    @staticmethod
    def send_leave_approval_notification(leave_request):
        """Send notification when leave is approved/rejected"""
        try:
            if apps.is_installed('notifications'):
                from notifications.signals import notify
                
                status_text = 'approved' if leave_request.status == 'approved' else 'rejected'
                
                notify.send(
                    sender=leave_request.manager,
                    recipient=leave_request.employee,
                    verb=f'leave request {status_text}',
                    action_object=leave_request,
                    description=f'Your {leave_request.get_leave_type_display()} request from {leave_request.start_date} to {leave_request.end_date} has been {status_text}'
                )
                
        except Exception as e:
            pass  # Fail silently for notifications


# Convenience functions for common operations
def get_employee_leave_balance(employee, leave_type, year=None):
    """Get employee's leave balance for a specific type and year"""
    if not year:
        year = date.today().year
    
    try:
        from employee.models.leave_models import EmployeeLeaveBalance
        return EmployeeLeaveBalance.objects.get(
            employee=employee,
            leave_type=leave_type,
            year=year
        )
    except Exception:
        return None


def create_leave_request(employee, leave_type, start_date, end_date, reason, duration='full_day', is_emergency=False):
    """Create a new leave request with validation"""
    try:
        from employee.models.leave_models import EmployeeLeaveRequest
        
        # Validate dates
        errors = LeaveValidator.validate_leave_dates(start_date, end_date)
        if errors:
            raise ValidationError(errors)
        
        # Calculate requested days
        requested_days = LeaveCalculator.calculate_leave_days(start_date, end_date, duration)
        
        # Validate balance (except for LOP)
        if leave_type != 'lop':
            is_valid, error_msg = LeaveValidator.validate_leave_balance(
                employee, leave_type, requested_days
            )
            if not is_valid:
                raise ValidationError(error_msg)
        
        # Check for overlapping requests
        has_overlap, overlapping = LeaveValidator.check_overlapping_requests(
            employee, start_date, end_date
        )
        if has_overlap:
            raise ValidationError(_('You have overlapping leave requests'))
        
        # Create the request
        leave_request = EmployeeLeaveRequest.objects.create(
            employee=employee,
            leave_type=leave_type,
            start_date=start_date,
            end_date=end_date,
            duration=duration,
            requested_days=requested_days,
            reason=reason,
            is_emergency=is_emergency
        )
        
        # Send notification
        LeaveNotificationManager.send_leave_application_notification(leave_request)
        
        return leave_request
        
    except Exception as e:
        raise ValidationError(str(e))
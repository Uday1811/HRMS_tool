"""
Custom leave models for employee-specific leave management
"""

from django.db import models
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from django.apps import apps
from .core import Employee


class EmployeeLeaveBalance(models.Model):
    """
    Model to track employee leave balances with strict separation
    """
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_balances')
    leave_type = models.CharField(max_length=20, choices=[
        ('cl', _('Casual Leave')),
        ('sl', _('Sick Leave')),
        ('el', _('Earned/Privilege Leave')),
        ('wfh', _('Work From Home')),
        ('comp_off', _('Comp-Off')),
        ('lop', _('Loss of Pay')),
    ])
    available_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    used_days = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    total_accrued = models.DecimalField(max_digits=5, decimal_places=1, default=0)
    year = models.IntegerField()
    
    class Meta:
        unique_together = ['employee', 'leave_type', 'year']
        verbose_name = _('Employee Leave Balance')
        verbose_name_plural = _('Employee Leave Balances')

    def __str__(self):
        return f"{self.employee} - {self.get_leave_type_display()} ({self.year})"

    def can_take_leave(self, days_requested):
        """Check if employee can take the requested leave days"""
        return self.available_days >= days_requested

    def deduct_leave(self, days_used):
        """Deduct leave days and update balance"""
        if not self.can_take_leave(days_used):
            raise ValidationError(_('Insufficient leave balance'))
        
        self.available_days -= days_used
        self.used_days += days_used
        self.save()

    def add_accrual(self, days_to_add):
        """Add accrued leave days"""
        self.available_days += days_to_add
        self.total_accrued += days_to_add
        self.save()


class EmployeeLeaveRequest(models.Model):
    """
    Enhanced leave request model with strict business rules
    """
    STATUS_CHOICES = [
        ('pending', _('Pending Manager Approval')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('cancelled', _('Cancelled')),
    ]

    LEAVE_TYPE_CHOICES = [
        ('cl', _('Casual Leave')),
        ('sl', _('Sick Leave')),
        ('el', _('Earned/Privilege Leave')),
        ('wfh', _('Work From Home')),
        ('comp_off', _('Comp-Off')),
        ('lop', _('Loss of Pay')),
    ]

    DURATION_CHOICES = [
        ('full_day', _('Full Day')),
        ('first_half', _('First Half')),
        ('second_half', _('Second Half')),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leave_requests')
    leave_type = models.CharField(max_length=10, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    duration = models.CharField(max_length=15, choices=DURATION_CHOICES, default='full_day')
    requested_days = models.DecimalField(max_digits=5, decimal_places=1)
    reason = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    
    # Manager approval fields
    manager = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True,
        related_name='managed_leave_requests'
    )
    manager_comments = models.TextField(blank=True)
    approved_date = models.DateTimeField(null=True, blank=True)
    
    # System fields
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_emergency = models.BooleanField(default=False)
    
    # File attachments
    attachment = models.FileField(upload_to='leave_attachments/', null=True, blank=True)

    class Meta:
        verbose_name = _('Employee Leave Request')
        verbose_name_plural = _('Employee Leave Requests')
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.employee} - {self.get_leave_type_display()} ({self.start_date} to {self.end_date})"

    def clean(self):
        """Validate leave request business rules"""
        super().clean()
        
        # Validate date range
        if self.start_date > self.end_date:
            raise ValidationError(_('Start date cannot be after end date'))
        
        # Calculate requested days
        self.calculate_requested_days()
        
        # Check leave balance only for paid/sick leave (not LOP)
        if self.leave_type in ['cl', 'sl', 'el', 'wfh', 'comp_off']:
            self.validate_leave_balance()

    def calculate_requested_days(self):
        """Calculate the number of leave days requested"""
        from datetime import timedelta
        
        if not self.start_date or not self.end_date:
            return
        
        # Calculate total days
        total_days = (self.end_date - self.start_date).days + 1
        
        # Adjust for half days
        if self.duration in ['first_half', 'second_half']:
            if self.start_date == self.end_date:
                total_days = 0.5
            else:
                # For multi-day requests with half day, calculate accordingly
                total_days = total_days - 0.5
        
        # Exclude weekends (optional - based on company policy)
        # This can be customized based on company requirements
        
        self.requested_days = total_days

    def validate_leave_balance(self):
        """Validate if employee has sufficient leave balance"""
        try:
            current_year = self.start_date.year
            balance = EmployeeLeaveBalance.objects.get(
                employee=self.employee,
                leave_type=self.leave_type,
                year=current_year
            )
            
            if not balance.can_take_leave(self.requested_days):
                raise ValidationError(
                    _('Insufficient %(leave_type)s balance. Available: %(available)s days, Requested: %(requested)s days') % {
                        'leave_type': self.get_leave_type_display(),
                        'available': balance.available_days,
                        'requested': self.requested_days
                    }
                )
        except EmployeeLeaveBalance.DoesNotExist:
            raise ValidationError(
                _('No %(leave_type)s balance found for year %(year)s') % {
                    'leave_type': self.get_leave_type_display(),
                    'year': self.start_date.year
                }
            )

    def approve_request(self, manager, comments=''):
        """Approve the leave request and deduct from balance"""
        from django.utils import timezone
        
        if self.status != 'pending':
            raise ValidationError(_('Only pending requests can be approved'))
        
        # Deduct from leave balance if not LOP
        if self.leave_type in ['cl', 'sl', 'el', 'wfh', 'comp_off']:
            try:
                balance = EmployeeLeaveBalance.objects.get(
                    employee=self.employee,
                    leave_type=self.leave_type,
                    year=self.start_date.year
                )
                balance.deduct_leave(self.requested_days)
            except EmployeeLeaveBalance.DoesNotExist:
                raise ValidationError(_('Leave balance not found'))
        
        # Update request status
        self.status = 'approved'
        self.manager = manager
        self.manager_comments = comments
        self.approved_date = timezone.now()
        self.save()

    def reject_request(self, manager, comments=''):
        """Reject the leave request"""
        if self.status != 'pending':
            raise ValidationError(_('Only pending requests can be rejected'))
        
        self.status = 'rejected'
        self.manager = manager
        self.manager_comments = comments
        self.save()

    def cancel_request(self):
        """Cancel the leave request and restore balance if already approved"""
        if self.status == 'approved' and self.leave_type in ['cl', 'sl', 'el', 'wfh', 'comp_off']:
            # Restore leave balance
            try:
                balance = EmployeeLeaveBalance.objects.get(
                    employee=self.employee,
                    leave_type=self.leave_type,
                    year=self.start_date.year
                )
                balance.available_days += self.requested_days
                balance.used_days -= self.requested_days
                balance.save()
            except EmployeeLeaveBalance.DoesNotExist:
                pass  # Balance not found, skip restoration
        
        self.status = 'cancelled'
        self.save()

    def get_manager(self):
        """Get the employee's reporting manager"""
        work_info = getattr(self.employee, 'employee_work_info', None)
        if work_info and work_info.reporting_manager_id:
            return work_info.reporting_manager_id
        return None

    def save(self, *args, **kwargs):
        """Override save to set manager and calculate days"""
        if not self.manager:
            self.manager = self.get_manager()
        
        # Calculate requested days before saving
        if self.start_date and self.end_date:
            self.calculate_requested_days()
        
        super().save(*args, **kwargs)


class CompOffRequest(models.Model):
    """
    Model to manage Comp-Off requests earned by working on holidays/weekends
    """
    STATUS_CHOICES = [
        ('pending', _('Pending Approval')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('used', _('Used')),
        ('expired', _('Expired')),
    ]

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='comp_off_requests')
    work_date = models.DateField(help_text=_("Date worked (Holiday/Weekend)"))
    expiry_date = models.DateField(null=True, blank=True)
    reason = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES, default='pending')
    
    # Manager approval
    manager = models.ForeignKey(
        Employee, 
        on_delete=models.SET_NULL, 
        null=True, 
        blank=True, 
        related_name='managed_comp_offs'
    )
    manager_comments = models.TextField(blank=True)
    approved_date = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = _('Comp-Off Request')
        verbose_name_plural = _('Comp-Off Requests')
        ordering = ['-work_date']

    def __str__(self):
        return f"{self.employee} - {self.work_date} ({self.status})"

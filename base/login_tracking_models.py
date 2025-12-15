"""
Login/Logout tracking models for Petabytz HRMS
"""
from django.contrib.auth.models import User
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone

from horilla.models import PetabytzModel


class UserLoginLog(PetabytzModel):
    """
    Model to track user login and logout activities
    """
    
    LOGIN_ACTION = 'login'
    LOGOUT_ACTION = 'logout'
    
    ACTION_CHOICES = [
        (LOGIN_ACTION, _('Login')),
        (LOGOUT_ACTION, _('Logout')),
    ]
    
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='login_logs',
        verbose_name=_('User')
    )
    action = models.CharField(
        max_length=10,
        choices=ACTION_CHOICES,
        verbose_name=_('Action')
    )
    timestamp = models.DateTimeField(
        default=timezone.now,
        verbose_name=_('Timestamp')
    )
    ip_address = models.GenericIPAddressField(
        null=True,
        blank=True,
        verbose_name=_('IP Address')
    )
    user_agent = models.TextField(
        null=True,
        blank=True,
        verbose_name=_('User Agent')
    )
    location = models.CharField(
        max_length=255,
        null=True,
        blank=True,
        verbose_name=_('Location')
    )
    session_key = models.CharField(
        max_length=40,
        null=True,
        blank=True,
        verbose_name=_('Session Key')
    )
    
    class Meta:
        verbose_name = _('User Login Log')
        verbose_name_plural = _('User Login Logs')
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['action', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.get_full_name() or self.user.username} - {self.get_action_display()} at {self.timestamp}"
    
    @property
    def employee_name(self):
        """Get the employee name if user is linked to an employee"""
        try:
            from employee.models import Employee
            employee = Employee.objects.get(employee_user_id=self.user)
            return f"{employee.employee_first_name} {employee.employee_last_name}".strip()
        except:
            return self.user.get_full_name() or self.user.username
    
    @property
    def formatted_timestamp(self):
        """Return formatted timestamp"""
        return self.timestamp.strftime('%Y-%m-%d %H:%M:%S')
"""
admin.py

This page is used to register base models with admins site.
"""

from django.contrib import admin
from simple_history.admin import SimpleHistoryAdmin

from base.models import (
    Announcement,
    Attachment,
    Company,
    CompanyLeaves,
    DashboardEmployeeCharts,
    Department,
    DynamicEmailConfiguration,
    DynamicPagination,
    EmailLog,
    EmployeeShift,
    EmployeeShiftDay,
    EmployeeShiftSchedule,
    EmployeeType,
    Holidays,
    JobPosition,
    JobRole,
    MultipleApprovalCondition,
    MultipleApprovalManagers,
    PenaltyAccounts,
    RotatingShift,
    RotatingShiftAssign,
    RotatingWorkType,
    RotatingWorkTypeAssign,
    ShiftRequest,
    ShiftRequestComment,
    Tags,
    WorkType,
    WorkTypeRequest,
    WorkTypeRequestComment,
)
from base.login_tracking_models import UserLoginLog

# Register your models here.

admin.site.register(Company)
admin.site.register(Department, SimpleHistoryAdmin)
admin.site.register(JobPosition)
admin.site.register(JobRole)
admin.site.register(EmployeeShift)
admin.site.register(EmployeeShiftSchedule)
admin.site.register(EmployeeShiftDay)
admin.site.register(EmployeeType)
admin.site.register(WorkType)
admin.site.register(RotatingWorkType)
admin.site.register(RotatingWorkTypeAssign)
admin.site.register(RotatingShift)
admin.site.register(RotatingShiftAssign)
admin.site.register(ShiftRequest)
admin.site.register(WorkTypeRequest)
admin.site.register(Tags)
admin.site.register(DynamicEmailConfiguration)
admin.site.register(MultipleApprovalManagers)
admin.site.register(ShiftRequestComment)
admin.site.register(WorkTypeRequestComment)
admin.site.register(DynamicPagination)
admin.site.register(Announcement)
admin.site.register(Attachment)
admin.site.register(EmailLog)
admin.site.register(DashboardEmployeeCharts)
admin.site.register(Holidays)
admin.site.register(CompanyLeaves)
admin.site.register(PenaltyAccounts)
admin.site.register(MultipleApprovalCondition)


@admin.register(UserLoginLog)
class UserLoginLogAdmin(admin.ModelAdmin):
    """Admin interface for User Login Logs"""
    
    list_display = [
        'employee_name', 
        'action', 
        'formatted_timestamp', 
        'ip_address', 
        'location'
    ]
    list_filter = [
        'action', 
        'timestamp', 
        'user__is_staff', 
        'user__is_active'
    ]
    search_fields = [
        'user__username', 
        'user__first_name', 
        'user__last_name', 
        'user__email',
        'ip_address',
        'location'
    ]
    readonly_fields = [
        'user', 
        'action', 
        'timestamp', 
        'ip_address', 
        'user_agent', 
        'location', 
        'session_key'
    ]
    ordering = ['-timestamp']
    date_hierarchy = 'timestamp'
    
    def has_add_permission(self, request):
        """Disable adding login logs manually"""
        return False
    
    def has_change_permission(self, request, obj=None):
        """Disable editing login logs"""
        return False
    
    def has_delete_permission(self, request, obj=None):
        """Only superusers can delete login logs"""
        return request.user.is_superuser

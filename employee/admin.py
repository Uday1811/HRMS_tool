"""
admin.py

This page is used to register the model with admins site.
"""

from django.contrib import admin
from django.contrib.auth.models import User
from django.contrib import messages
from simple_history.admin import SimpleHistoryAdmin
from .utils import generate_employee_password, send_welcome_email, get_login_instructions

from employee.models import (
    Actiontype,
    BonusPoint,
    DisciplinaryAction,
    Employee,
    EmployeeBankDetails,
    EmployeeNote,
    EmployeeTag,
    EmployeeWorkInformation,
    Policy,
    PolicyMultipleFile,
    HandbookSection,
    PolicySection,
)

# Import leave models if they exist
try:
    from employee.models.leave_models import EmployeeLeaveBalance, EmployeeLeaveRequest
    LEAVE_MODELS_AVAILABLE = True
except ImportError:
    LEAVE_MODELS_AVAILABLE = False

# Register your models here.

# admin.site.register(Employee)
admin.site.register(EmployeeBankDetails)
admin.site.register([EmployeeNote, EmployeeTag, PolicyMultipleFile, Policy, BonusPoint])
admin.site.register([DisciplinaryAction, Actiontype])
admin.site.register([HandbookSection, PolicySection])


class EmployeeWorkInformationAdmin(SimpleHistoryAdmin):
    list_display = (
        "employee_id",
        "department_id",
        "job_position_id",
        "job_role_id",
        "reporting_manager_id",
        "shift_id",
        "work_type_id",
        "company_id",
    )
    search_fields = (
        "employee_id__employee_first_name",
        "employee_id__employee_last_name",
    )


# Leave Management Admin Classes
if LEAVE_MODELS_AVAILABLE:
    
    @admin.register(EmployeeLeaveBalance)
    class EmployeeLeaveBalanceAdmin(admin.ModelAdmin):
        list_display = (
            'employee',
            'leave_type',
            'year',
            'available_days',
            'used_days',
            'total_accrued',
            'utilization_percentage'
        )
        list_filter = ('leave_type', 'year')
        search_fields = (
            'employee__employee_first_name',
            'employee__employee_last_name',
            'employee__badge_id'
        )
        readonly_fields = ('utilization_percentage',)
        
        def utilization_percentage(self, obj):
            if obj.total_accrued > 0:
                return f"{(obj.used_days / obj.total_accrued * 100):.1f}%"
            return "0%"
        utilization_percentage.short_description = 'Utilization %'
        
        def get_queryset(self, request):
            return super().get_queryset(request).select_related('employee')
        
        actions = ['reset_balances', 'accrue_monthly_leaves']
        
        def reset_balances(self, request, queryset):
            """Reset selected leave balances"""
            count = 0
            for balance in queryset:
                balance.available_days = balance.total_accrued
                balance.used_days = 0
                balance.save()
                count += 1
            
            self.message_user(
                request,
                f'Successfully reset {count} leave balances.',
                messages.SUCCESS
            )
        reset_balances.short_description = "Reset selected leave balances"
        
        def accrue_monthly_leaves(self, request, queryset):
            """Add monthly accrual to selected balances"""
            from employee.leave_utils import LeaveCalculator
            
            count = 0
            for balance in queryset:
                monthly_accrual = LeaveCalculator.get_monthly_accrual(
                    balance.employee, 
                    balance.leave_type
                )
                balance.add_accrual(monthly_accrual)
                count += 1
            
            self.message_user(
                request,
                f'Successfully accrued monthly leaves for {count} balances.',
                messages.SUCCESS
            )
        accrue_monthly_leaves.short_description = "Accrue monthly leaves for selected balances"

    
    @admin.register(EmployeeLeaveRequest)
    class EmployeeLeaveRequestAdmin(admin.ModelAdmin):
        list_display = (
            'employee',
            'leave_type',
            'start_date',
            'end_date',
            'requested_days',
            'status',
            'manager',
            'created_at',
            'is_emergency'
        )
        list_filter = (
            'status',
            'leave_type',
            'is_emergency',
            'created_at',
            'start_date'
        )
        search_fields = (
            'employee__employee_first_name',
            'employee__employee_last_name',
            'employee__badge_id',
            'reason'
        )
        readonly_fields = (
            'requested_days',
            'created_at',
            'updated_at',
            'approved_date'
        )
        
        fieldsets = (
            ('Leave Request Information', {
                'fields': (
                    'employee',
                    'leave_type',
                    'start_date',
                    'end_date',
                    'duration',
                    'requested_days',
                    'reason',
                    'is_emergency',
                    'attachment'
                )
            }),
            ('Approval Information', {
                'fields': (
                    'status',
                    'manager',
                    'manager_comments',
                    'approved_date'
                )
            }),
            ('System Information', {
                'fields': (
                    'created_at',
                    'updated_at'
                ),
                'classes': ('collapse',)
            })
        )
        
        def get_queryset(self, request):
            return super().get_queryset(request).select_related(
                'employee', 'manager'
            )
        
        actions = ['approve_requests', 'reject_requests', 'export_to_excel']
        
        def approve_requests(self, request, queryset):
            """Approve selected leave requests"""
            count = 0
            errors = 0
            
            for leave_request in queryset.filter(status='pending'):
                try:
                    # Get the requesting user as manager (admin approval)
                    manager_employee = getattr(request.user, 'employee_get', None)
                    if manager_employee:
                        leave_request.approve_request(manager_employee, 'Approved by admin')
                        count += 1
                    else:
                        errors += 1
                except Exception as e:
                    errors += 1
            
            if count > 0:
                self.message_user(
                    request,
                    f'Successfully approved {count} leave requests.',
                    messages.SUCCESS
                )
            if errors > 0:
                self.message_user(
                    request,
                    f'Failed to approve {errors} leave requests.',
                    messages.ERROR
                )
        approve_requests.short_description = "Approve selected leave requests"
        
        def reject_requests(self, request, queryset):
            """Reject selected leave requests"""
            count = 0
            
            for leave_request in queryset.filter(status='pending'):
                try:
                    manager_employee = getattr(request.user, 'employee_get', None)
                    if manager_employee:
                        leave_request.reject_request(manager_employee, 'Rejected by admin')
                        count += 1
                except Exception:
                    pass
            
            self.message_user(
                request,
                f'Successfully rejected {count} leave requests.',
                messages.SUCCESS
            )
        reject_requests.short_description = "Reject selected leave requests"
        
        def export_to_excel(self, request, queryset):
            """Export selected leave requests to Excel"""
            import pandas as pd
            from django.http import HttpResponse
            
            # Prepare data for export
            data = []
            for leave_request in queryset:
                data.append({
                    'Employee': str(leave_request.employee),
                    'Badge ID': leave_request.employee.badge_id,
                    'Leave Type': leave_request.get_leave_type_display(),
                    'Start Date': leave_request.start_date,
                    'End Date': leave_request.end_date,
                    'Duration': leave_request.get_duration_display(),
                    'Requested Days': leave_request.requested_days,
                    'Status': leave_request.get_status_display(),
                    'Manager': str(leave_request.manager) if leave_request.manager else '',
                    'Reason': leave_request.reason,
                    'Emergency': 'Yes' if leave_request.is_emergency else 'No',
                    'Applied Date': leave_request.created_at.date(),
                    'Approved Date': leave_request.approved_date.date() if leave_request.approved_date else '',
                })
            
            # Create DataFrame and Excel response
            df = pd.DataFrame(data)
            response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
            response['Content-Disposition'] = 'attachment; filename=leave_requests.xlsx'
            
            with pd.ExcelWriter(response, engine='openpyxl') as writer:
                df.to_excel(writer, index=False, sheet_name='Leave Requests')
            
            return response
        export_to_excel.short_description = "Export selected requests to Excel"


class EmployeeAdmin(admin.ModelAdmin):
    list_display = (
        "badge_id",
        "employee_first_name",
        "employee_last_name",
        "employee_user_id",
        "is_active",
    )

    search_fields = (
        "badge_id",
        "employee_user_id__username",
        "employee_first_name",
        "employee_last_name",
    )

    list_filter = ("is_active",)

    ordering = ("employee_first_name", "employee_last_name")

    def save_model(self, request, obj, form, change):
        """
        Automatically create User account if employee_user_id is not set
        """
        if not change and not obj.employee_user_id:  # Only for new employees
            # Create username from email or badge_id
            username = obj.email if obj.email else f"emp_{obj.badge_id}"
            
            # Check if user already exists
            if User.objects.filter(username=username).exists():
                username = f"{username}_{obj.badge_id}"
            
            # Generate temporary password using utility function
            temp_password = generate_employee_password(obj)
            
            # Create new User
            user = User.objects.create_user(
                username=username,
                email=obj.email,
                first_name=obj.employee_first_name,
                last_name=obj.employee_last_name or "",
                password=temp_password
            )
            
            obj.employee_user_id = user
            
            # Try to send welcome email
            email_sent = False
            if obj.email:
                email_sent = send_welcome_email(obj, username, temp_password)
            
            # Show success message with login instructions
            login_message = get_login_instructions(obj, username, temp_password)
            
            if email_sent:
                login_message += "\n\n✅ Welcome email sent to employee's email address."
            elif obj.email:
                login_message += "\n\n⚠️ Failed to send welcome email. Please share credentials manually."
            else:
                login_message += "\n\n📧 No email provided. Please share credentials manually."
            
            messages.success(request, login_message)
        
        super().save_model(request, obj, form, change)

    def delete_view(self, request, object_id, extra_context=None):
        extra_context = extra_context or {}
        extra_context["custom_message"] = (
            "Are you sure you want to delete this item? This action cannot be undone."
        )
        return super().delete_view(request, object_id, extra_context=extra_context)


admin.site.register(Employee, EmployeeAdmin)
admin.site.register(EmployeeWorkInformation, EmployeeWorkInformationAdmin)

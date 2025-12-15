# Enhanced Leave Management System

## Overview

This enhanced leave management system provides comprehensive leave functionality for employees in the Petabytz HRMS, similar to modern HRMS solutions like Keka. It includes advanced features for leave application, approval workflows, balance tracking, and automated accruals.

## Features

### ✅ 1. Leave Types Support
- **CL** - Casual Leave
- **SL** - Sick Leave  
- **EL/PL** - Earned/Privilege Leave
- **WFH** - Work From Home
- **Comp-Off** - Compensatory Leave (earned from weekend/holiday work)
- **LOP** - Loss of Pay (automatic when no balance available)

### ✅ 2. Leave Application System
- **Smart Application Form** with real-time balance checking
- **Duration Options**: Full Day, First Half, Second Half, Quarter Day
- **Auto-calculation** of leave days excluding weekends and holidays
- **File Attachment Support** for medical certificates and documents
- **Emergency Leave** flag for urgent requests
- **Validation Rules** with configurable advance notice requirements
- **Overlap Detection** to prevent conflicting leave requests

### ✅ 3. Leave Balance & Accrual Management
- **Visual Balance Cards** showing available/used/carry-forward days
- **Progress Bars** for quick balance overview
- **Automated Monthly Accrual** (1.5 days/month for paid leave, 1 day/month for sick leave)
- **Pro-rata Accrual** for new joiners based on joining date
- **Carry Forward Rules** with configurable limits
- **Leave Encashment** support for unused leaves
- **Real-time Balance Updates** when selecting leave types

### ✅ 4. Multi-level Approval Workflow
- **Step 1**: Employee submits leave request
- **Step 2**: Direct manager review and approval/rejection
- **Step 3**: HR approval for policy compliance (optional)
- **Step 4**: Automatic integration with attendance and payroll
- **Status Tracking**: Requested → Manager Review → HR Approval → Auto Integration
- **Manager Actions**: Approve, Reject, Request More Information, Add Comments
- **Email Notifications** at each step of the workflow

### ✅ 5. Leave History & Analytics
- **Comprehensive Request Table** with advanced filtering
- **Status-based Filtering**: All, Approved, Pending, Rejected, Cancelled
- **Detailed Request Information** with duration breakdown
- **Leave Usage Analytics** with monthly/yearly trends
- **Department-wise Reports** for managers and HR
- **Export Functionality** to Excel/PDF formats

### ✅ 6. Comp-Off Management
- **Earned Comp-Off Tracking** from weekend/holiday work
- **Automatic Comp-Off Generation** when working on holidays
- **Validity Period Management** (configurable, default 45 days)
- **Usage Limits** (max per month/day restrictions)
- **Redemption as Leave** with manager approval
- **Expiry Notifications** for unused comp-offs

### ✅ 7. Holiday Integration
- **Company Holiday Calendar** integration
- **Location-based Holidays** support
- **Automatic Exclusion** from leave calculations
- **Holiday Conflict Detection** during application
- **Upcoming Holidays Widget** in employee dashboard

### ✅ 8. Advanced Features
- **LOP Calculation** when leave balance is insufficient
- **Weekend Exclusion** from leave calculations
- **Half-day Leave Support** with precise calculations
- **Emergency Leave Workflow** bypass for urgent situations
- **Leave Policy Compliance** with configurable rules
- **Audit Trail** for all leave transactions

## Technical Implementation

### Models

#### EmployeeLeaveBalance
```python
class EmployeeLeaveBalance(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPE_CHOICES)
    available_days = models.DecimalField(max_digits=5, decimal_places=1)
    used_days = models.DecimalField(max_digits=5, decimal_places=1)
    total_accrued = models.DecimalField(max_digits=5, decimal_places=1)
    year = models.IntegerField()
```

#### EmployeeLeaveRequest
```python
class EmployeeLeaveRequest(models.Model):
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    leave_type = models.CharField(max_length=10, choices=LEAVE_TYPE_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField()
    duration = models.CharField(max_length=15, choices=DURATION_CHOICES)
    requested_days = models.DecimalField(max_digits=5, decimal_places=1)
    reason = models.TextField()
    status = models.CharField(max_length=15, choices=STATUS_CHOICES)
    manager = models.ForeignKey(Employee, on_delete=models.SET_NULL, null=True)
    # ... additional fields
```

### API Endpoints

#### Leave Application
```
POST /employee/api/leave/apply/
```
**Parameters:**
- `leave_type`: Type of leave (paid, sick, lop)
- `start_date`: Leave start date (YYYY-MM-DD)
- `end_date`: Leave end date (YYYY-MM-DD)
- `duration`: full_day, first_half, second_half
- `reason`: Reason for leave
- `emergency`: Boolean for emergency requests
- `attachments`: File uploads (optional)

#### Leave Cancellation
```
POST /employee/api/leave/cancel/{request_id}/
```

### Management Commands

#### Setup Leave System
```bash
python manage.py setup_leave_system --year 2024 --paid-leave-days 18 --sick-leave-days 12
```

#### Monthly Leave Accrual
```bash
python manage.py accrue_monthly_leaves --month 12 --year 2024
```

### Utility Classes

#### LeaveCalculator
- `calculate_working_days()`: Calculate working days excluding weekends/holidays
- `calculate_leave_days()`: Calculate leave days with duration consideration
- `get_monthly_accrual()`: Get monthly accrual rates
- `calculate_pro_rata_accrual()`: Calculate pro-rata for new joiners

#### LeaveValidator
- `validate_leave_dates()`: Validate date ranges and advance notice
- `validate_leave_balance()`: Check sufficient balance
- `check_overlapping_requests()`: Detect conflicting requests

#### LeaveReportGenerator
- `get_employee_leave_summary()`: Comprehensive employee report
- `get_department_leave_report()`: Department-wide analytics

## Configuration

### Leave Policies
Configure leave policies in `employee/leave_utils.py`:

```python
# Monthly accrual rates
accrual_rates = {
    'paid': 1.5,  # 1.5 days per month (18 days per year)
    'sick': 1.0,  # 1 day per month (12 days per year)
}

# Advance notice requirements
MINIMUM_ADVANCE_DAYS = 2

# Carry forward limits
CARRY_FORWARD_LIMITS = {
    'paid': 5,  # Max 5 days carry forward
    'sick': 0,  # No carry forward for sick leave
}
```

### Approval Workflow
Configure approval hierarchy in employee work information:
- Set `reporting_manager_id` for direct manager approval
- Configure HR approval roles in Django groups
- Set up email notifications in notification settings

## Usage Examples

### Employee Leave Application
```javascript
// Apply for leave via AJAX
fetch('/employee/api/leave/apply/', {
    method: 'POST',
    body: formData,
    headers: {
        'X-CSRFToken': getCookie('csrftoken')
    }
})
.then(response => response.json())
.then(data => {
    if (data.success) {
        showNotification('Leave application submitted successfully!', 'success');
    }
});
```

### Manager Approval
```python
# Approve leave request
leave_request = EmployeeLeaveRequest.objects.get(id=request_id)
leave_request.approve_request(manager, 'Approved for vacation')
```

### Generate Reports
```python
from employee.leave_utils import LeaveReportGenerator

# Employee summary
summary = LeaveReportGenerator.get_employee_leave_summary(employee, 2024)

# Department report
report = LeaveReportGenerator.get_department_leave_report(department, 2024)
```

## Installation & Setup

### 1. Run Migrations
```bash
python manage.py makemigrations employee
python manage.py migrate
```

### 2. Setup Initial Leave Balances
```bash
python manage.py setup_leave_system --year 2024
```

### 3. Configure Cron Job for Monthly Accrual
```bash
# Add to crontab for monthly execution on 1st of each month
0 0 1 * * /path/to/python /path/to/manage.py accrue_monthly_leaves
```

### 4. Configure Email Settings
Update Django settings for email notifications:
```python
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'your-smtp-server.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = 'your-email@company.com'
EMAIL_HOST_PASSWORD = 'your-password'
```

## Admin Interface

### Leave Balance Management
- View and edit employee leave balances
- Bulk reset balances for new year
- Manual accrual adjustments
- Utilization percentage tracking

### Leave Request Management
- Approve/reject leave requests in bulk
- Export leave data to Excel
- View detailed request information
- Manager comment tracking

## Integration Points

### Attendance Integration
- Approved leaves automatically marked in attendance
- LOP calculation affects payroll
- Weekend and holiday exclusions

### Payroll Integration
- Leave deductions calculated automatically
- LOP impacts salary calculations
- Leave encashment processing

### Notification Integration
- Real-time notifications for all stakeholders
- Email alerts for pending approvals
- Status update notifications

## Customization

### Adding New Leave Types
1. Update `LEAVE_TYPE_CHOICES` in models
2. Add accrual rates in `LeaveCalculator`
3. Update validation rules if needed
4. Add UI elements for new type

### Custom Approval Workflows
1. Extend `EmployeeLeaveRequest` model
2. Add custom approval methods
3. Update notification logic
4. Modify UI workflow display

### Company-specific Policies
1. Modify validation rules in `LeaveValidator`
2. Update accrual calculations
3. Customize carry-forward logic
4. Add policy-specific validations

## Troubleshooting

### Common Issues

1. **Leave balance not showing**
   - Run `setup_leave_system` command
   - Check employee work information setup

2. **Accrual not working**
   - Verify cron job setup
   - Check employee joining dates
   - Run manual accrual command

3. **Approval notifications not sent**
   - Verify email settings
   - Check notification app installation
   - Verify manager assignment

### Debug Commands
```bash
# Check leave balances
python manage.py shell
>>> from employee.models.leave_models import EmployeeLeaveBalance
>>> EmployeeLeaveBalance.objects.filter(employee__badge_id='PEP002')

# Test leave calculation
>>> from employee.leave_utils import LeaveCalculator
>>> LeaveCalculator.calculate_working_days(start_date, end_date)
```

## Performance Considerations

- Use database indexes on frequently queried fields
- Implement caching for leave balance calculations
- Optimize queries with select_related/prefetch_related
- Consider archiving old leave data annually

## Security

- Validate all user inputs
- Implement proper permission checks
- Audit trail for all leave transactions
- Secure file upload handling
- CSRF protection on all forms

## Future Enhancements

- Mobile app integration
- Advanced analytics dashboard
- Machine learning for leave pattern analysis
- Integration with external calendar systems
- Automated policy compliance checking
- Multi-currency leave encashment
- Advanced reporting with charts and graphs

## Support

For technical support or feature requests, please contact the development team or create an issue in the project repository.
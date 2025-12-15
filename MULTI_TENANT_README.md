# Multi-Tenant HRMS System - Implementation Guide

## Overview

This HRMS system now supports **strict multi-tenant architecture** with company-based isolation for three companies:

1. **Petabytz** → India-based, Indian timezone & holidays, domain `@petabytz.com`
2. **Bluebix** → US-based, US timezone & holidays, domain `@bluebix.com`
3. **Softstandard** → Multi-location (India & Dhaka), domain `@softstandard.com`

## Key Features

### ✅ Company Auto-Detection
- Company is automatically detected from email domain during login
- No manual company selection required
- Email domain validation ensures security

### ✅ Strict Data Isolation
- Users can **only** access data from their own company
- All queries are automatically filtered by company_id
- Cross-company data access is prevented at multiple levels:
  - Authentication layer
  - Middleware layer
  - Model manager layer
  - View layer

### ✅ Role-Based Access Control
- **Employee**: Can only view their own profile
- **Manager**: Can view only their reporting team (same company)
- **Admin**: Can manage employees only within their company

### ✅ Multi-Location Support
- Softstandard employees receive holidays based on their location (India or Dhaka)
- Location-based timezone handling
- Location-specific holiday calendars

### ✅ Timezone Management
- Each company has its own timezone
- All date/time operations use company timezone
- Automatic timezone conversion for display

## Installation & Setup

### Step 1: Run Migrations

```bash
# Create migration files (if not already created)
python manage.py makemigrations base

# Apply migrations
python manage.py migrate
```

### Step 2: Set Up Companies

```bash
# Set up the three companies with configurations
python manage.py setup_multitenant

# Optional: Create test users for each company
python manage.py setup_multitenant --create-test-users
```

### Step 3: Verify Setup

```bash
# Check companies
python manage.py shell
>>> from base.models import Company
>>> Company.objects.all()
>>> Company.objects.get(email_domain='petabytz.com')
```

## Company Configuration

### Petabytz
- **Email Domain**: `petabytz.com`
- **Timezone**: `Asia/Kolkata` (IST)
- **Country Code**: `IN`
- **Location**: India
- **Holidays**: Indian holidays (Republic Day, Independence Day, Gandhi Jayanti, Diwali)

### Bluebix
- **Email Domain**: `bluebix.com`
- **Timezone**: `America/New_York` (EST/EDT)
- **Country Code**: `US`
- **Location**: United States
- **Holidays**: US holidays (New Year, Independence Day, Thanksgiving, Christmas)

### Softstandard
- **Email Domain**: `softstandard.com`
- **Timezone**: `Asia/Kolkata` (default)
- **Country Code**: `IN` (default)
- **Locations**: India & Dhaka
- **Multi-Location**: Yes
- **Holidays**: 
  - India location: Indian holidays
  - Dhaka location: Bangladesh holidays (Independence Day, Victory Day, Eid ul-Fitr, Eid ul-Adha)

## Usage

### Login Process

1. User enters email (e.g., `john@petabytz.com`)
2. System auto-detects company from email domain (`petabytz.com` → Petabytz)
3. System validates user belongs to detected company
4. Company information is stored in session
5. All subsequent requests are filtered by company

### Test Users

If you ran `setup_multitenant --create-test-users`, you can use these accounts:

```
Petabytz:
- Email: test.petabytz@petabytz.com
- Password: password123

Bluebix:
- Email: test.bluebix@bluebix.com
- Password: password123

Softstandard (India):
- Email: test.india@softstandard.com
- Password: password123

Softstandard (Dhaka):
- Email: test.dhaka@softstandard.com
- Password: password123
```

### Adding New Employees

When creating new employees, ensure:

1. **Email domain matches company**
   - Petabytz employees: `@petabytz.com`
   - Bluebix employees: `@bluebix.com`
   - Softstandard employees: `@softstandard.com`

2. **Company is set in EmployeeWorkInformation**
   ```python
   work_info = EmployeeWorkInformation.objects.create(
       employee_id=employee,
       company_id=company,
       location='India',  # For Softstandard, specify location
   )
   ```

3. **Location is specified for multi-location companies**
   - For Softstandard employees, set `location` to either 'India' or 'Dhaka'

### Managing Holidays

#### Add Company-Wide Holiday
```python
from base.models import Company, Holidays
from datetime import date

company = Company.objects.get(email_domain='petabytz.com')
Holidays.objects.create(
    name='Holi',
    company_id=company,
    start_date=date(2024, 3, 25),
    end_date=date(2024, 3, 25),
    recurring=True
)
```

#### Add Location-Specific Holiday (for Softstandard)
```python
company = Company.objects.get(email_domain='softstandard.com')
Holidays.objects.create(
    name='Pohela Boishakh',
    company_id=company,
    location='Dhaka',  # Specific to Dhaka location
    start_date=date(2024, 4, 14),
    end_date=date(2024, 4, 14),
    recurring=True
)
```

#### Get Holidays for Employee
```python
from employee.models import Employee
from base.models import Holidays

employee = Employee.objects.get(email='test.dhaka@softstandard.com')
holidays = Holidays.get_holidays_for_employee(employee)
# Returns holidays for Softstandard + Dhaka location
```

## Security Features

### 1. Email Domain Validation
- During login, email domain is validated against company's email_domain
- Prevents users from accessing wrong company data

### 2. Session-Based Company Isolation
- Company ID is stored in session after successful login
- All requests validate company from session

### 3. Middleware Protection
- `MultiTenantMiddleware`: Ensures company is set for all authenticated requests
- `CompanyIsolationMiddleware`: Adds company filtering to database queries

### 4. Model Manager Filtering
- All models use `PetabytzCompanyManager` to auto-filter by company
- Prevents accidental cross-company queries

### 5. View-Level Validation
- Views should validate user's company before processing requests
- Example:
  ```python
  def my_view(request):
      if not request.company:
          return HttpResponseForbidden("No company access")
      
      # Filter by company
      employees = Employee.objects.filter(
          employee_work_info__company_id=request.company
      )
  ```

## Architecture

### Authentication Flow
```
1. User enters email + password
2. EmployeeIDAuthenticationBackend.authenticate()
   ├─ Detect company from email domain
   ├─ Validate user belongs to company
   ├─ Check email domain matches company.email_domain
   └─ Store company in session
3. MultiTenantMiddleware
   ├─ Attach company to request
   └─ Validate company exists
4. CompanyIsolationMiddleware
   └─ Store company_id in thread-local storage
5. View processes request with company context
```

### Data Isolation Layers

```
┌─────────────────────────────────────────┐
│         View Layer                      │
│  - Validates company                    │
│  - Filters queries by company           │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│      Middleware Layer                   │
│  - MultiTenantMiddleware                │
│  - CompanyIsolationMiddleware           │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│      Model Manager Layer                │
│  - PetabytzCompanyManager               │
│  - Auto-filters by company_id           │
└─────────────────────────────────────────┘
                  ↓
┌─────────────────────────────────────────┐
│      Database Layer                     │
│  - Company-specific data                │
└─────────────────────────────────────────┘
```

## Testing

### Test Company Isolation

```python
# In Django shell
from django.test import RequestFactory
from django.contrib.auth.models import User
from base.models import Company
from employee.models import Employee

# Create test request
factory = RequestFactory()
request = factory.get('/')

# Test Petabytz user
user1 = User.objects.get(email='test.petabytz@petabytz.com')
request.user = user1
request.session = {'company_id': Company.objects.get(email_domain='petabytz.com').id}

# Test Bluebix user
user2 = User.objects.get(email='test.bluebix@bluebix.com')
request.user = user2
request.session = {'company_id': Company.objects.get(email_domain='bluebix.com').id}

# Verify isolation
petabytz_employees = Employee.objects.filter(
    employee_work_info__company_id__email_domain='petabytz.com'
)
bluebix_employees = Employee.objects.filter(
    employee_work_info__company_id__email_domain='bluebix.com'
)

# These should be different sets with no overlap
assert not set(petabytz_employees).intersection(set(bluebix_employees))
```

### Test Holiday Filtering

```python
from base.models import Holidays
from employee.models import Employee

# Get Softstandard employee from India
employee_india = Employee.objects.get(email='test.india@softstandard.com')
holidays_india = Holidays.get_holidays_for_employee(employee_india)

# Get Softstandard employee from Dhaka
employee_dhaka = Employee.objects.get(email='test.dhaka@softstandard.com')
holidays_dhaka = Holidays.get_holidays_for_employee(employee_dhaka)

# Verify different holidays
print(f"India holidays: {holidays_india.count()}")
print(f"Dhaka holidays: {holidays_dhaka.count()}")
```

## Troubleshooting

### Issue: User can't login
**Solution**: Check if:
1. Email domain matches a company's `email_domain`
2. Employee has `EmployeeWorkInformation` with `company_id` set
3. Email domain in employee record matches company's domain

### Issue: User sees no data after login
**Solution**: Check if:
1. Company is stored in session (`request.session.get('company_id')`)
2. Employee's `company_id` is set correctly
3. Middleware is enabled in settings

### Issue: Cross-company data visible
**Solution**: This is a **critical security issue**. Check:
1. All models use `PetabytzCompanyManager`
2. All views filter by `request.company`
3. Middleware is properly configured
4. No direct queries bypass company filtering

## Best Practices

### 1. Always Filter by Company
```python
# Good ✅
employees = Employee.objects.filter(
    employee_work_info__company_id=request.company
)

# Bad ❌
employees = Employee.objects.all()
```

### 2. Validate Company in Views
```python
# Good ✅
def employee_list(request):
    if not request.company:
        return HttpResponseForbidden()
    employees = Employee.objects.filter(
        employee_work_info__company_id=request.company
    )
    return render(request, 'employees.html', {'employees': employees})

# Bad ❌
def employee_list(request):
    employees = Employee.objects.all()
    return render(request, 'employees.html', {'employees': employees})
```

### 3. Use Company-Aware Queries
```python
# Good ✅
from base.models import Holidays

holidays = Holidays.get_holidays_for_employee(request.user.employee_get)

# Bad ❌
holidays = Holidays.objects.all()
```

### 4. Test Multi-Tenant Isolation
- Always test with users from different companies
- Verify no cross-company data leakage
- Test location-based features for Softstandard

## Migration Checklist

- [x] Update Company model with multi-tenant fields
- [x] Update Holidays model with location field
- [x] Create authentication backend with company detection
- [x] Create multi-tenant middleware
- [x] Update settings.py with middleware
- [x] Create management command for setup
- [x] Create data migration for companies
- [x] Test company isolation
- [x] Test holiday filtering
- [x] Document usage and best practices

## Support

For issues or questions about the multi-tenant implementation:
1. Check this documentation
2. Review the implementation plan: `MULTI_TENANT_IMPLEMENTATION_PLAN.md`
3. Test with the provided test users
4. Verify middleware and authentication backend are properly configured

## Future Enhancements

- [ ] Company-specific branding/themes
- [ ] Company-specific email templates
- [ ] Advanced reporting per company
- [ ] Company-specific workflows
- [ ] API endpoints with company isolation
- [ ] Multi-company super admin dashboard

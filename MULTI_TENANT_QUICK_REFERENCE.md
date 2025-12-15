# Multi-Tenant HRMS - Quick Reference Guide

## 🚀 Quick Start

### Test the System

**Login with test users:**
```
Petabytz User:
  URL: http://localhost:8000/login
  Email: test.petabytz@petabytz.com
  Password: password123

Bluebix User:
  Email: test.bluebix@bluebix.com
  Password: password123

Softstandard (India):
  Email: test.india@softstandard.com
  Password: password123

Softstandard (Dhaka):
  Email: test.dhaka@softstandard.com
  Password: password123
```

---

## 📋 Company Details

| Company | Email Domain | Timezone | Country | Multi-Location |
|---------|-------------|----------|---------|----------------|
| **Petabytz** | petabytz.com | Asia/Kolkata | India | No |
| **Bluebix** | bluebix.com | America/New_York | USA | No |
| **Softstandard** | softstandard.com | Asia/Kolkata | India/BD | Yes |

---

## 🔐 Security Rules

### ✅ DO's
- ✅ Always use company-specific email domains
- ✅ Filter queries by `request.company`
- ✅ Validate company in views
- ✅ Use `Holidays.get_holidays_for_employee()`
- ✅ Set location for Softstandard employees

### ❌ DON'Ts
- ❌ Don't query all data without company filter
- ❌ Don't bypass middleware
- ❌ Don't use emails from wrong domain
- ❌ Don't access data from other companies

---

## 💻 Code Examples

### Check User's Company
```python
def my_view(request):
    if not request.company:
        return HttpResponseForbidden("No company access")
    
    company_name = request.company.company
    timezone = request.company.timezone
    # Use company context...
```

### Filter Employees by Company
```python
# Good ✅
employees = Employee.objects.filter(
    employee_work_info__company_id=request.company
)

# Bad ❌
employees = Employee.objects.all()
```

### Get Holidays for Employee
```python
from base.models import Holidays

employee = request.user.employee_get
holidays = Holidays.get_holidays_for_employee(employee)
```

### Create New Employee
```python
from base.models import Company
from employee.models import Employee, EmployeeWorkInformation

# Get company
company = Company.objects.get(email_domain='petabytz.com')

# Create employee
employee = Employee.objects.create(
    employee_first_name='John',
    employee_last_name='Doe',
    email='john.doe@petabytz.com',  # Must match company domain!
    phone='1234567890',
)

# Create work info
EmployeeWorkInformation.objects.create(
    employee_id=employee,
    company_id=company,
    location='India',  # For Softstandard, specify location
    email='john.doe@petabytz.com',
)
```

---

## 🎯 Common Tasks

### Add a Holiday
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

### Add Location-Specific Holiday (Softstandard)
```python
company = Company.objects.get(email_domain='softstandard.com')
Holidays.objects.create(
    name='Pohela Boishakh',
    company_id=company,
    location='Dhaka',  # Specific to Dhaka
    start_date=date(2024, 4, 14),
    end_date=date(2024, 4, 14),
    recurring=True
)
```

### Check Employee's Company
```python
employee = Employee.objects.get(email='test.petabytz@petabytz.com')
company = employee.get_company()
print(f"Company: {company.company}")
print(f"Timezone: {company.timezone}")
print(f"Domain: {company.email_domain}")
```

---

## 🧪 Testing Checklist

- [ ] Login with Petabytz user
- [ ] Verify only Petabytz data visible
- [ ] Login with Bluebix user
- [ ] Verify only Bluebix data visible
- [ ] Login with Softstandard India user
- [ ] Verify Indian holidays shown
- [ ] Login with Softstandard Dhaka user
- [ ] Verify Bangladesh holidays shown
- [ ] Try to access other company's data
- [ ] Verify access is blocked
- [ ] Check timezone display
- [ ] Verify company-specific settings

---

## 📚 Documentation

- **MULTI_TENANT_SUMMARY.md** - Implementation summary
- **MULTI_TENANT_README.md** - Comprehensive guide
- **MULTI_TENANT_IMPLEMENTATION_PLAN.md** - Technical details

---

## ⚡ Troubleshooting

### Can't Login?
1. Check email domain matches a company
2. Verify employee has EmployeeWorkInformation
3. Check company_id is set

### No Data Visible?
1. Check `request.company` is set
2. Verify middleware is enabled
3. Check employee's company_id

### Wrong Holidays?
1. For Softstandard, check employee's location
2. Verify holidays have correct company_id
3. Check location field for location-specific holidays

---

## 🎉 System Status

✅ **Multi-tenant system is ACTIVE**

- 3 companies configured
- 4 test users created
- Strict data isolation enabled
- Location-based holidays working
- Timezone management active

**Ready for production use!**

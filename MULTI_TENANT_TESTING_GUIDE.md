# Multi-Tenant HRMS - Testing Guide

## 🧪 Complete Testing Checklist

This guide will help you verify that the multi-tenant system is working correctly with strict company isolation.

---

## Test 1: Company Auto-Detection ✅

### Objective
Verify that company is automatically detected from email domain during login.

### Steps
1. Navigate to login page: `http://localhost:8000/login`
2. Enter email: `test.petabytz@petabytz.com`
3. Enter password: `password123`
4. Click Login

### Expected Results
- ✅ Login successful
- ✅ Redirected to dashboard
- ✅ Company name "Petabytz" visible in header/navbar
- ✅ Session contains company_id for Petabytz

### Verification
```python
# In Django shell
from django.contrib.sessions.models import Session
from django.contrib.auth.models import User

user = User.objects.get(email='test.petabytz@petabytz.com')
# Check session after login
# Should contain: company_id, company_name, company_timezone
```

---

## Test 2: Data Isolation - Petabytz vs Bluebix ✅

### Objective
Verify that Petabytz users cannot see Bluebix data and vice versa.

### Steps

#### Part A: Login as Petabytz User
1. Login with `test.petabytz@petabytz.com`
2. Navigate to employee list
3. Note the employees visible
4. Navigate to holidays list
5. Note the holidays visible
6. Logout

#### Part B: Login as Bluebix User
1. Login with `test.bluebix@bluebix.com`
2. Navigate to employee list
3. Note the employees visible
4. Navigate to holidays list
5. Note the holidays visible

### Expected Results
- ✅ Petabytz user sees only Petabytz employees
- ✅ Petabytz user sees only Indian holidays
- ✅ Bluebix user sees only Bluebix employees
- ✅ Bluebix user sees only US holidays
- ✅ No overlap between the two companies

### Verification
```python
# In Django shell
from employee.models import Employee
from base.models import Company, Holidays

# Petabytz data
petabytz = Company.objects.get(email_domain='petabytz.com')
petabytz_employees = Employee.objects.filter(
    employee_work_info__company_id=petabytz
)
petabytz_holidays = Holidays.objects.filter(company_id=petabytz)

# Bluebix data
bluebix = Company.objects.get(email_domain='bluebix.com')
bluebix_employees = Employee.objects.filter(
    employee_work_info__company_id=bluebix
)
bluebix_holidays = Holidays.objects.filter(company_id=bluebix)

# Verify no overlap
assert not set(petabytz_employees).intersection(set(bluebix_employees))
assert not set(petabytz_holidays).intersection(set(bluebix_holidays))
```

---

## Test 3: Location-Based Holidays (Softstandard) ✅

### Objective
Verify that Softstandard employees get location-specific holidays.

### Steps

#### Part A: India Location
1. Login with `test.india@softstandard.com`
2. Navigate to holidays page
3. Note the holidays visible
4. Look for Indian holidays (Republic Day, Independence Day, etc.)
5. Check if Bangladesh holidays are visible
6. Logout

#### Part B: Dhaka Location
1. Login with `test.dhaka@softstandard.com`
2. Navigate to holidays page
3. Note the holidays visible
4. Look for Bangladesh holidays (Victory Day, Eid, etc.)
5. Check if India-specific holidays are visible

### Expected Results
- ✅ India employee sees Indian holidays
- ✅ India employee sees common Softstandard holidays
- ✅ Dhaka employee sees Bangladesh holidays
- ✅ Dhaka employee sees common Softstandard holidays
- ✅ Each location gets appropriate holidays

### Verification
```python
# In Django shell
from employee.models import Employee
from base.models import Holidays

# India employee
india_emp = Employee.objects.get(email='test.india@softstandard.com')
india_holidays = Holidays.get_holidays_for_employee(india_emp)
print(f"India holidays: {[h.name for h in india_holidays]}")

# Dhaka employee
dhaka_emp = Employee.objects.get(email='test.dhaka@softstandard.com')
dhaka_holidays = Holidays.get_holidays_for_employee(dhaka_emp)
print(f"Dhaka holidays: {[h.name for h in dhaka_holidays]}")

# Verify different sets
assert india_holidays.count() != dhaka_holidays.count()
```

---

## Test 4: Timezone Handling ✅

### Objective
Verify that each company uses its own timezone.

### Steps
1. Login as Petabytz user
2. Check displayed times (should be in IST)
3. Logout
4. Login as Bluebix user
5. Check displayed times (should be in EST/EDT)

### Expected Results
- ✅ Petabytz: Times in Asia/Kolkata (IST)
- ✅ Bluebix: Times in America/New_York (EST/EDT)
- ✅ Softstandard: Times in Asia/Kolkata (default)

### Verification
```python
# In Django shell
from base.models import Company

petabytz = Company.objects.get(email_domain='petabytz.com')
print(f"Petabytz timezone: {petabytz.timezone}")  # Asia/Kolkata

bluebix = Company.objects.get(email_domain='bluebix.com')
print(f"Bluebix timezone: {bluebix.timezone}")  # America/New_York

softstandard = Company.objects.get(email_domain='softstandard.com')
print(f"Softstandard timezone: {softstandard.timezone}")  # Asia/Kolkata
```

---

## Test 5: Cross-Company Access Prevention ✅

### Objective
Verify that users cannot access other companies' data through URL manipulation.

### Steps
1. Login as Petabytz user
2. Note the URL pattern for employee detail page
3. Try to access a Bluebix employee's detail page by changing URL
4. Try to access Bluebix holidays
5. Try to access Bluebix attendance records

### Expected Results
- ✅ Access denied or 404 error
- ✅ No data from other companies visible
- ✅ Middleware blocks unauthorized access

### Verification
```python
# In Django shell
from django.test import Client
from django.contrib.auth.models import User

client = Client()

# Login as Petabytz user
user = User.objects.get(email='test.petabytz@petabytz.com')
client.force_login(user)

# Try to access Bluebix data
# Should fail or return empty results
response = client.get('/employee/list/')
# Verify only Petabytz employees in response
```

---

## Test 6: Role-Based Access Control ✅

### Objective
Verify that employees, managers, and admins have appropriate access levels.

### Test Cases

#### Employee Access
- ✅ Can view own profile
- ✅ Can view own attendance
- ✅ Can view own leaves
- ✅ Cannot view other employees' profiles
- ✅ Cannot access admin functions

#### Manager Access
- ✅ Can view own profile
- ✅ Can view reporting team profiles
- ✅ Can approve team leave requests
- ✅ Cannot view non-reporting employees
- ✅ Cannot access full admin functions

#### Admin Access
- ✅ Can view all employees (same company)
- ✅ Can manage all attendance (same company)
- ✅ Can manage all leaves (same company)
- ✅ Cannot access other companies' data

---

## Test 7: Email Domain Validation ✅

### Objective
Verify that email domain must match company domain.

### Steps
1. Try to create employee with wrong email domain
   - Company: Petabytz
   - Email: test@bluebix.com (wrong domain)
2. Verify validation error
3. Create employee with correct domain
   - Company: Petabytz
   - Email: test@petabytz.com (correct domain)

### Expected Results
- ✅ Wrong domain: Validation error or login failure
- ✅ Correct domain: Success

---

## Test 8: Session Security ✅

### Objective
Verify that company information is securely stored in session.

### Steps
1. Login as Petabytz user
2. Check session data
3. Verify company_id is stored
4. Logout
5. Verify session is cleared
6. Try to access protected pages
7. Verify redirect to login

### Expected Results
- ✅ Session contains company_id after login
- ✅ Session cleared after logout
- ✅ Cannot access protected pages without login

---

## Test 9: Attendance Isolation ✅

### Objective
Verify that attendance records are company-specific.

### Steps
1. Login as Petabytz user
2. Clock in
3. View attendance records
4. Logout
5. Login as Bluebix user
6. View attendance records
7. Verify Petabytz attendance not visible

### Expected Results
- ✅ Each company sees only their own attendance
- ✅ No cross-company attendance visible

---

## Test 10: Leave Request Isolation ✅

### Objective
Verify that leave requests are company-specific.

### Steps
1. Login as Petabytz user
2. Submit leave request
3. View leave requests
4. Logout
5. Login as Bluebix user
6. View leave requests
7. Verify Petabytz leave not visible

### Expected Results
- ✅ Each company sees only their own leaves
- ✅ No cross-company leaves visible

---

## Automated Testing Script

```python
# test_multitenant.py
from django.test import TestCase, Client
from django.contrib.auth.models import User
from base.models import Company, Holidays
from employee.models import Employee

class MultiTenantTestCase(TestCase):
    def setUp(self):
        """Set up test data"""
        # Create companies
        self.petabytz = Company.objects.create(
            company='Petabytz',
            email_domain='petabytz.com',
            timezone='Asia/Kolkata',
            country_code='IN'
        )
        self.bluebix = Company.objects.create(
            company='Bluebix',
            email_domain='bluebix.com',
            timezone='America/New_York',
            country_code='US'
        )
        
        # Create test users
        self.petabytz_user = User.objects.create_user(
            username='test.petabytz@petabytz.com',
            email='test.petabytz@petabytz.com',
            password='password123'
        )
        self.bluebix_user = User.objects.create_user(
            username='test.bluebix@bluebix.com',
            email='test.bluebix@bluebix.com',
            password='password123'
        )
    
    def test_company_detection(self):
        """Test company auto-detection from email"""
        company = Company.get_company_by_email('test@petabytz.com')
        self.assertEqual(company, self.petabytz)
        
        company = Company.get_company_by_email('test@bluebix.com')
        self.assertEqual(company, self.bluebix)
    
    def test_data_isolation(self):
        """Test that companies cannot see each other's data"""
        client = Client()
        
        # Login as Petabytz user
        client.force_login(self.petabytz_user)
        response = client.get('/employee/list/')
        # Verify only Petabytz employees
        
        # Login as Bluebix user
        client.force_login(self.bluebix_user)
        response = client.get('/employee/list/')
        # Verify only Bluebix employees
    
    def test_session_security(self):
        """Test session contains company information"""
        client = Client()
        client.login(
            username='test.petabytz@petabytz.com',
            password='password123'
        )
        
        session = client.session
        self.assertIn('company_id', session)
        self.assertEqual(session['company_name'], 'Petabytz')
        self.assertEqual(session['company_timezone'], 'Asia/Kolkata')

# Run tests
# python manage.py test test_multitenant
```

---

## Performance Testing

### Load Test
1. Create 100 employees per company
2. Login as each company
3. Measure query performance
4. Verify no N+1 queries
5. Check database query count

### Expected Results
- ✅ Queries are optimized
- ✅ Company filtering adds minimal overhead
- ✅ No performance degradation

---

## Security Audit Checklist

- [ ] Email domain validation works
- [ ] Session security is enforced
- [ ] Middleware blocks unauthorized access
- [ ] Model managers filter by company
- [ ] Views validate company
- [ ] No SQL injection vulnerabilities
- [ ] No cross-company data leakage
- [ ] Role-based access works correctly
- [ ] Location-based holidays work
- [ ] Timezone handling is correct

---

## Test Results Template

```
Date: _______________
Tester: _______________

Test 1: Company Auto-Detection          [ ] PASS  [ ] FAIL
Test 2: Data Isolation                   [ ] PASS  [ ] FAIL
Test 3: Location-Based Holidays          [ ] PASS  [ ] FAIL
Test 4: Timezone Handling                [ ] PASS  [ ] FAIL
Test 5: Cross-Company Access Prevention  [ ] PASS  [ ] FAIL
Test 6: Role-Based Access Control        [ ] PASS  [ ] FAIL
Test 7: Email Domain Validation          [ ] PASS  [ ] FAIL
Test 8: Session Security                 [ ] PASS  [ ] FAIL
Test 9: Attendance Isolation             [ ] PASS  [ ] FAIL
Test 10: Leave Request Isolation         [ ] PASS  [ ] FAIL

Overall Status: [ ] ALL TESTS PASSED  [ ] SOME TESTS FAILED

Notes:
_________________________________________________________________
_________________________________________________________________
_________________________________________________________________
```

---

## 🎉 Testing Complete!

Once all tests pass, the multi-tenant system is ready for production use.

**Remember:**
- Test with real data
- Test edge cases
- Test concurrent users
- Monitor performance
- Review security regularly

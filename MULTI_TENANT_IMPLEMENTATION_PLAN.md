# Multi-Tenant HRMS System Implementation Plan

## Overview
This document outlines the implementation of a strict multi-tenant HRMS system with company-based isolation for Petabytz, Bluebix, and Softstandard.

## Company Configuration

### 1. Petabytz
- **Domain**: @petabytz.com
- **Location**: India
- **Timezone**: Asia/Kolkata (IST)
- **Holidays**: Indian holidays

### 2. Bluebix
- **Domain**: @bluebix.com
- **Location**: United States
- **Timezone**: America/New_York (EST/EDT)
- **Holidays**: US holidays

### 3. Softstandard
- **Domain**: @softstandard.com
- **Locations**: India & Dhaka
- **Timezone**: 
  - India: Asia/Kolkata (IST)
  - Dhaka: Asia/Dhaka (BST)
- **Holidays**: Location-based (India or Bangladesh)

## Implementation Steps

### Phase 1: Database Schema Updates

#### 1.1 Enhance Company Model
- Add `email_domain` field (unique, for auto-detection)
- Add `timezone` field (default timezone for company)
- Add `country_code` field (for holiday calendar)
- Add `is_multi_location` field (for companies like Softstandard)

#### 1.2 Create CompanyHoliday Model
- Link holidays to specific companies
- Support location-based holidays for multi-location companies
- Fields: company, holiday_name, date, location (optional), is_recurring

#### 1.3 Update Employee Model
- Ensure `location` field in EmployeeWorkInformation is properly used
- Add validation to prevent cross-company data access

### Phase 2: Authentication & Authorization

#### 2.1 Enhanced Authentication Backend
- Auto-detect company from email domain during login
- Store company_id in session
- Validate user belongs to detected company

#### 2.2 Company Middleware
- Add middleware to enforce company isolation on every request
- Filter all queries by company_id automatically
- Prevent cross-company data access

#### 2.3 Permission System
- Employee: Can only view own profile
- Manager: Can view reporting team only (within same company)
- Admin: Can manage all employees within their company only

### Phase 3: Data Isolation

#### 3.1 Query Filtering
- Update all model managers to filter by company_id
- Ensure PetabytzCompanyManager is used consistently
- Add company_id to all relevant models:
  - Attendance records
  - Leave requests
  - Announcements
  - Payroll records
  - Employee profiles

#### 3.2 View-Level Security
- Add company validation in all views
- Ensure queryset filtering by company_id
- Add permission checks for cross-company access attempts

### Phase 4: Timezone & Holiday Management

#### 4.1 Timezone Handling
- Use company timezone for all date/time operations
- Display times in user's company timezone
- Handle timezone conversion for multi-location companies

#### 4.2 Holiday Calendar
- Create holiday management interface
- Support location-based holidays for Softstandard
- Auto-apply holidays based on employee location

### Phase 5: UI/UX Updates

#### 5.1 Login Page
- Auto-detect company from email domain
- Display company-specific branding (optional)
- Show appropriate timezone information

#### 5.2 Dashboard
- Display only company-specific data
- Show company-specific announcements
- Filter all lists by company

#### 5.3 Admin Interface
- Restrict admin to manage only their company
- Add company selector for super admins (if needed)

### Phase 6: Testing & Validation

#### 6.1 Security Testing
- Test cross-company data access prevention
- Validate session isolation
- Test permission boundaries

#### 6.2 Functional Testing
- Test login with all three company domains
- Verify timezone handling
- Validate holiday calendar functionality
- Test manager/employee/admin permissions

## Security Rules

### Critical Security Requirements

1. **No Cross-Company Data Access**
   - All queries must filter by company_id
   - No employee can view another company's data
   - No admin can manage another company's employees

2. **Company Auto-Detection**
   - Company must be detected from email domain
   - No manual company selection during login
   - Session must store and validate company_id

3. **Role-Based Access**
   - Employee: Own profile only
   - Manager: Own team only (same company)
   - Admin: All employees in same company only

4. **Data Isolation**
   - Attendance: Company-specific
   - Leaves: Company-specific
   - Announcements: Company-specific
   - Payroll: Company-specific
   - Profiles: Company-specific

## Migration Strategy

### Step 1: Create New Models
- CompanyHoliday model
- Update Company model with new fields

### Step 2: Data Migration
- Populate email_domain for existing companies
- Set timezone for existing companies
- Create default holiday calendars

### Step 3: Update Existing Code
- Update authentication backend
- Add company middleware
- Update all views with company filtering

### Step 4: Testing
- Test with sample users from each company
- Verify data isolation
- Validate timezone handling

### Step 5: Deployment
- Backup database
- Run migrations
- Deploy updated code
- Monitor for issues

## Files to Modify

### Models
- `base/models.py` - Update Company model
- `base/models.py` - Add CompanyHoliday model
- `employee/models/core.py` - Ensure company isolation

### Authentication
- `base/employee_auth_backend.py` - Add company detection
- `base/middleware.py` - Add company isolation middleware

### Views
- `employee/views.py` - Add company filtering
- `attendance/views/*.py` - Add company filtering
- `leave/views.py` - Add company filtering
- `payroll/views.py` - Add company filtering

### Templates
- Update all templates to respect company isolation
- Add company-specific branding (optional)

## Configuration

### Environment Variables
```
# Company-specific settings
PETABYTZ_DOMAIN=petabytz.com
BLUEBIX_DOMAIN=bluebix.com
SOFTSTANDARD_DOMAIN=softstandard.com

# Timezone settings
PETABYTZ_TIMEZONE=Asia/Kolkata
BLUEBIX_TIMEZONE=America/New_York
SOFTSTANDARD_TIMEZONE_INDIA=Asia/Kolkata
SOFTSTANDARD_TIMEZONE_DHAKA=Asia/Dhaka
```

## Success Criteria

1. ✅ Company auto-detected from email domain during login
2. ✅ Users can only access data from their own company
3. ✅ Attendance records are company-specific
4. ✅ Leave requests are company-specific
5. ✅ Announcements are company-specific
6. ✅ Payroll data is company-specific
7. ✅ Employees see only their own profile
8. ✅ Managers see only their reporting team (same company)
9. ✅ Admins manage only their company's employees
10. ✅ Softstandard employees get location-based holidays
11. ✅ Timezone handling works correctly for all companies
12. ✅ No cross-company data leakage under any circumstance

## Next Steps

1. Review and approve this implementation plan
2. Create database migrations
3. Implement company detection in authentication
4. Add company middleware for data isolation
5. Update all views and queries
6. Test thoroughly
7. Deploy to production

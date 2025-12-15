"""
Custom authentication backend for Employee ID login with multi-tenant support
"""
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.models import User
from employee.models import Employee
from base.models import Company


class EmployeeIDAuthenticationBackend(BaseBackend):
    """
    Custom authentication backend that allows login with Employee ID (badge_id)
    with multi-tenant company isolation
    """
    
    def authenticate(self, request, username=None, password=None, **kwargs):
        """
        Authenticate user by Employee ID (badge_id) or regular username
        Auto-detect company from email domain for multi-tenant isolation
        """
        if username is None or password is None:
            return None
        
        user = None
        company = None
        
        # First try to find user by Employee badge_id
        try:
            employee = Employee.objects.get(badge_id=username)
            user = employee.employee_user_id
            if user and user.check_password(password):
                # Get company from employee
                company = employee.get_company()
                # Validate company matches email domain
                if company and company.email_domain:
                    email = employee.get_email()
                    if email and '@' in email:
                        email_domain = email.split('@')[1].lower()
                        if email_domain != company.email_domain.lower():
                            # Email domain mismatch - security violation
                            return None
                # Store company in session
                if request and company:
                    request.session['company_id'] = company.id
                    request.session['company_name'] = company.company
                    request.session['company_timezone'] = company.timezone
                return user
        except Employee.DoesNotExist:
            pass
            
        # If not found by badge_id, try regular username authentication
        try:
            user = User.objects.get(username=username)
            if user.check_password(password):
                # Get company from user's employee profile
                try:
                    employee = user.employee_get
                    company = employee.get_company()
                    # Validate company matches email domain
                    if company and company.email_domain:
                        email = employee.get_email()
                        if email and '@' in email:
                            email_domain = email.split('@')[1].lower()
                            if email_domain != company.email_domain.lower():
                                # Email domain mismatch - security violation
                                return None
                    # Store company in session
                    if request and company:
                        request.session['company_id'] = company.id
                        request.session['company_name'] = company.company
                        request.session['company_timezone'] = company.timezone
                except Employee.DoesNotExist:
                    pass
                return user
        except User.DoesNotExist:
            pass
            
        # Also try email authentication
        try:
            user = User.objects.get(email=username)
            if user.check_password(password):
                # Auto-detect company from email domain
                company = Company.get_company_by_email(username)
                
                # Get employee and validate company
                try:
                    employee = user.employee_get
                    employee_company = employee.get_company()
                    
                    # Ensure detected company matches employee's company
                    if company and employee_company and company.id != employee_company.id:
                        # Company mismatch - security violation
                        return None
                    
                    # Use employee's company if detected company is None
                    if not company:
                        company = employee_company
                        
                except Employee.DoesNotExist:
                    pass
                
                # Store company in session
                if request and company:
                    request.session['company_id'] = company.id
                    request.session['company_name'] = company.company
                    request.session['company_timezone'] = company.timezone
                    
                return user
        except User.DoesNotExist:
            pass
            
        return None
    
    def get_user(self, user_id):
        """
        Get user by ID
        """
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None

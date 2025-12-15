"""
Multi-tenant middleware for company-based data isolation
"""
from django.http import HttpResponseForbidden
from django.shortcuts import redirect
from django.urls import reverse
from base.models import Company


class MultiTenantMiddleware:
    """
    Middleware to enforce company-based multi-tenant isolation.
    Ensures users can only access data from their own company.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        # URLs that don't require company isolation
        self.exempt_urls = [
            '/login',
            '/logout',
            '/admin/',
            '/static/',
            '/media/',
            '/api/auth/',
        ]
    
    def __call__(self, request):
        # Check if URL is exempt from company isolation
        if any(request.path.startswith(url) for url in self.exempt_urls):
            return self.get_response(request)
        
        # Check if user is authenticated
        if not request.user.is_authenticated:
            return self.get_response(request)
        
        # Get company from session
        company_id = request.session.get('company_id')
        
        # If no company in session, try to get from user's employee profile
        if not company_id:
            try:
                employee = request.user.employee_get
                company = employee.get_company()
                if company:
                    # Store in session for future requests
                    request.session['company_id'] = company.id
                    request.session['company_name'] = company.company
                    request.session['company_timezone'] = company.timezone
                    company_id = company.id
            except:
                pass
        
        # Attach company to request for easy access
        if company_id:
            try:
                request.company = Company.objects.get(id=company_id)
            except Company.DoesNotExist:
                # Invalid company in session - clear it
                request.session.pop('company_id', None)
                request.session.pop('company_name', None)
                request.session.pop('company_timezone', None)
                request.company = None
        else:
            request.company = None
        
        response = self.get_response(request)
        return response
    
    def process_view(self, request, view_func, view_args, view_kwargs):
        """
        Additional validation before view execution
        """
        # Skip for exempt URLs
        if any(request.path.startswith(url) for url in self.exempt_urls):
            return None
        
        # Skip for unauthenticated users
        if not request.user.is_authenticated:
            return None
        
        # Ensure company is set for authenticated users
        if not hasattr(request, 'company') or not request.company:
            # User doesn't have a company - this is a security issue
            # Log them out and redirect to login
            from django.contrib.auth import logout
            logout(request)
            return redirect(reverse('login'))
        
        return None


class CompanyIsolationMiddleware:
    """
    Middleware to add company filtering context to all database queries.
    This provides an additional layer of security for multi-tenant isolation.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
    
    def __call__(self, request):
        # Store company_id in thread-local storage for use in model managers
        from horilla import horilla_middlewares
        
        if hasattr(request, 'company') and request.company:
            # Store company in thread-local for access in model managers
            if not hasattr(horilla_middlewares._thread_locals, 'company_id'):
                horilla_middlewares._thread_locals.company_id = request.company.id
            else:
                horilla_middlewares._thread_locals.company_id = request.company.id
        
        response = self.get_response(request)
        
        # Clean up thread-local storage
        if hasattr(horilla_middlewares._thread_locals, 'company_id'):
            delattr(horilla_middlewares._thread_locals, 'company_id')
        
        return response

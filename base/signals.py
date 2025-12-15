"""
Django signals for tracking user login/logout activities
"""
from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone
from .login_tracking_models import UserLoginLog


def get_client_ip(request):
    """Get the client IP address from request"""
    x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
    if x_forwarded_for:
        ip = x_forwarded_for.split(',')[0]
    else:
        ip = request.META.get('REMOTE_ADDR')
    return ip


def get_location_from_ip(ip_address):
    """
    Get location from IP address
    You can integrate with services like GeoIP2, ipapi, etc.
    For now, returning a placeholder
    """
    # TODO: Integrate with a geolocation service
    # Example with ipapi.co (requires requests library):
    # try:
    #     import requests
    #     response = requests.get(f'https://ipapi.co/{ip_address}/json/')
    #     data = response.json()
    #     return f"{data.get('city', '')}, {data.get('region', '')}, {data.get('country_name', '')}"
    # except:
    #     return "Unknown"
    
    return "Location tracking not configured"


@receiver(user_logged_in)
def log_user_login(sender, request, user, **kwargs):
    """Log user login activity"""
    ip_address = get_client_ip(request)
    user_agent = request.META.get('HTTP_USER_AGENT', '')
    location = get_location_from_ip(ip_address) if ip_address else None
    
    UserLoginLog.objects.create(
        user=user,
        action=UserLoginLog.LOGIN_ACTION,
        timestamp=timezone.now(),
        ip_address=ip_address,
        user_agent=user_agent,
        location=location,
        session_key=request.session.session_key
    )


@receiver(user_logged_out)
def log_user_logout(sender, request, user, **kwargs):
    """Log user logout activity"""
    if user and user.is_authenticated:
        ip_address = get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        location = get_location_from_ip(ip_address) if ip_address else None
        
        UserLoginLog.objects.create(
            user=user,
            action=UserLoginLog.LOGOUT_ACTION,
            timestamp=timezone.now(),
            ip_address=ip_address,
            user_agent=user_agent,
            location=location,
            session_key=request.session.session_key
        )
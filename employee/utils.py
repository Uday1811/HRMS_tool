"""
Utility functions for employee management
"""
import random
import string
from django.core.mail import send_mail
from django.conf import settings
from django.template.loader import render_to_string


def generate_employee_password(employee):
    """
    Generate a secure temporary password for new employees
    """
    if employee.phone and len(str(employee.phone)) >= 6:
        # Use phone number as password
        return str(employee.phone)
    else:
        # Generate pattern: FirstName + Badge suffix + @123
        first_name = employee.employee_first_name.lower() if employee.employee_first_name else "emp"
        badge_suffix = str(employee.badge_id)[-4:] if employee.badge_id else "0001"
        return f"{first_name}{badge_suffix}@123"


def generate_random_password(length=8):
    """
    Generate a random secure password
    """
    characters = string.ascii_letters + string.digits + "!@#$%"
    return ''.join(random.choice(characters) for _ in range(length))


def send_welcome_email(employee, username, password):
    """
    Send welcome email with login credentials to new employee
    """
    if not employee.email:
        return False
        
    subject = "Welcome to Petabytz HRMS - Your Login Credentials"
    
    context = {
        'employee_name': f"{employee.employee_first_name} {employee.employee_last_name or ''}".strip(),
        'username': username,
        'employee_id': employee.badge_id,
        'email': employee.email,
        'password': password,
        'login_url': 'http://localhost:8000/login/',  # Update with your actual domain
    }
    
    # Create email content
    message = f"""
    Dear {context['employee_name']},

    Welcome to Petabytz HRMS! Your employee account has been created successfully.

    LOGIN CREDENTIALS:
    • Username: {username}
    • Employee ID: {employee.badge_id}
    • Email: {employee.email}
    • Password: {password}

    You can login using any of the following methods:
    1. Username + Password
    2. Employee ID + Password
    3. Email + Password

    Login URL: {context['login_url']}

    IMPORTANT SECURITY NOTICE:
    - Please change your password immediately after your first login
    - Keep your credentials secure and do not share them with others
    - Contact IT support if you have any issues accessing your account

    Best regards,
    HR Team
    """
    
    try:
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [employee.email],
            fail_silently=False,
        )
        return True
    except Exception as e:
        print(f"Failed to send welcome email: {e}")
        return False


def get_login_instructions(employee, username, password):
    """
    Get formatted login instructions for display
    """
    return f"""
    🎉 Employee created successfully! 

    📋 LOGIN CREDENTIALS:
    • Username: {username}
    • Employee ID: {employee.badge_id}
    • Email: {employee.email}
    • Password: {password}

    💡 The employee can login using:
    1. Username + Password
    2. Employee ID + Password  
    3. Email + Password

    ⚠️ IMPORTANT: 
    - Share these credentials securely with the employee
    - Ask them to change the password on first login
    - Consider sending credentials via email if configured
    """
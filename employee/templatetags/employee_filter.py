from datetime import timedelta

from django import template

register = template.Library()


@register.filter(name="add_days")
def add_days(value, days):
    # Check if value is not None before adding days
    if value is not None:
        return value + timedelta(days=days)
    else:
        return None


@register.filter(name="edit_accessibility")
def edit_accessibility(emp):
    return emp.default_accessibility.filter(feature="profile_edit").exists()


@register.filter(name="subtract")
def subtract(value, arg):
    """Subtract arg from value"""
    try:
        return float(value) - float(arg)
    except (ValueError, TypeError):
        return 0


@register.filter(name="widthsubtract")
def widthsubtract(total, available):
    """Calculate used leave days (total - available)"""
    try:
        return float(total) - float(available)
    except (ValueError, TypeError):
        return 0

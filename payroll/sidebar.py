"""
payroll/sidebar.py
"""

from django.urls import reverse
from django.utils.translation import gettext_lazy as trans

MENU = trans("Payroll")
IMG_SRC = "images/ui/wallet-outline.svg"

SUBMENUS = [
    {
        "menu": trans("Payslips"),
        "redirect": reverse("view-payslips"),
    },
]

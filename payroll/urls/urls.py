"""
urls.py
"""

from django.urls import path
from django.views.generic import RedirectView
from payroll.views import simple_payslip_views

urlpatterns = [
    path("view-payslips/", simple_payslip_views.view_payslips, name="view-payslips"),
    path("upload-payslip/", simple_payslip_views.upload_payslip, name="upload-payslip"),
    path("delete-payslip/<int:id>/", simple_payslip_views.delete_payslip, name="delete-payslip"),
    
    # Redirect old finance/payroll URLs to the new simple payslips view
    path("view-payroll-dashboard/", RedirectView.as_view(pattern_name='view-payslips', permanent=True)),
    path("finance-dashboard/", RedirectView.as_view(pattern_name='view-payslips', permanent=True)),
    path("dashboard/", RedirectView.as_view(pattern_name='view-payslips', permanent=True)),
    path("view-payslip/", RedirectView.as_view(pattern_name='view-payslips', permanent=True)),
]

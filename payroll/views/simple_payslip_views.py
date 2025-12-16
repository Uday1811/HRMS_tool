from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.core.paginator import Paginator
from django import forms
from payroll.models.models import EmployeePayslip
from employee.models import Employee

class EmployeePayslipForm(forms.ModelForm):
    class Meta:
        model = EmployeePayslip
        fields = ['employee', 'pay_period', 'document']
        widgets = {
            'pay_period': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'employee': forms.Select(attrs={'class': 'form-control'}),
            'document': forms.FileInput(attrs={'class': 'form-control'}),
        }

@login_required
def view_payslips(request):
    """
    View for employees to see their own payslips with bank details and financial info.
    Admins can see all payslips.
    """
    # Get employee object
    employee = None
    bank_details = None
    work_info = None
    
    if request.user.has_perm('payroll.add_employeepayslip'): # Check if admin/manager
        payslips = EmployeePayslip.objects.all()
    elif hasattr(request.user, 'employee_get'):
        employee = request.user.employee_get
        payslips = EmployeePayslip.objects.filter(employee=employee)
        
        # Get bank details
        if hasattr(employee, 'employee_bank_details'):
            bank_details = employee.employee_bank_details
        
        # Get work information (for UAN, CTC, etc.)
        if hasattr(employee, 'employee_work_info'):
            work_info = employee.employee_work_info
    else:
        payslips = EmployeePayslip.objects.none()

    paginator = Paginator(payslips, 20)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'payslips': page_obj,
        'employee': employee,
        'bank_details': bank_details,
        'work_info': work_info,
    }

    return render(request, 'payroll/view_payslips.html', context)

@login_required
@permission_required('payroll.add_employeepayslip', raise_exception=True) 
def upload_payslip(request):
    """
    View for admins to upload a payslip.
    """
    if request.method == 'POST':
        form = EmployeePayslipForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, _('Payslip uploaded successfully.'))
            return redirect('view-payslips')
        else:
             messages.error(request, _('Error uploading payslip.'))
    else:
        form = EmployeePayslipForm()
    
    return render(request, 'payroll/upload_payslip.html', {'form': form})

@login_required
@permission_required('payroll.delete_employeepayslip', raise_exception=True)
def delete_payslip(request, id):
    """
    View to delete a payslip.
    """
    payslip = get_object_or_404(EmployeePayslip, id=id)
    payslip.delete()
    messages.success(request, _('Payslip deleted successfully.'))
    return redirect('view-payslips')

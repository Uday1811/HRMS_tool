"""
Views for Handbook and Policy Management
"""
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required, permission_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from django.http import JsonResponse
from employee.models import HandbookSection, PolicySection


@login_required
def handbook_dashboard(request):
    """
    Display handbook sections. HR/Admin can edit, employees can only view.
    """
    # Default demo content for each section
    DEFAULT_CONTENT = {
        'company_rules': '''
            <h3>Welcome to Our Company</h3>
            <p>This section contains important company rules and regulations that all employees must follow.</p>
            
            <h3>Working Hours</h3>
            <ul>
                <li>Standard working hours: 9:00 AM - 6:00 PM</li>
                <li>Lunch break: 1:00 PM - 2:00 PM</li>
                <li>Tea breaks: 11:00 AM and 4:00 PM (15 minutes each)</li>
            </ul>
            
            <h3>Workplace Conduct</h3>
            <ul>
                <li>Maintain professional behavior at all times</li>
                <li>Respect colleagues and their workspace</li>
                <li>Follow company security protocols</li>
                <li>Report any safety concerns immediately</li>
            </ul>
            
            <p><em>Note: This is draft content. Please contact HR for the complete company rules.</em></p>
        ''',
        'conduct_guidelines': '''
            <h3>Professional Conduct</h3>
            <p>Our company values professionalism, integrity, and respect in all workplace interactions.</p>
            
            <h3>Expected Behaviors</h3>
            <ul>
                <li>Treat all colleagues with respect and dignity</li>
                <li>Communicate professionally in all formats</li>
                <li>Maintain confidentiality of sensitive information</li>
                <li>Avoid conflicts of interest</li>
                <li>Report unethical behavior through proper channels</li>
            </ul>
            
            <h3>Prohibited Behaviors</h3>
            <ul>
                <li>Harassment or discrimination of any kind</li>
                <li>Misuse of company resources</li>
                <li>Disclosure of confidential information</li>
                <li>Workplace violence or threats</li>
            </ul>
            
            <p><em>Note: This is draft content. Please contact HR for complete conduct guidelines.</em></p>
        ''',
        'dress_code': '''
            <h3>Dress Code Policy</h3>
            <p>We maintain a business casual dress code to ensure a professional work environment.</p>
            
            <h3>General Guidelines</h3>
            <ul>
                <li>Business casual attire is expected for office days</li>
                <li>Formal business attire for client meetings</li>
                <li>Casual attire permitted on designated casual Fridays</li>
                <li>Clothing should be clean, neat, and appropriate</li>
            </ul>
            
            <h3>Acceptable Attire</h3>
            <ul>
                <li>Collared shirts, blouses, or professional tops</li>
                <li>Dress pants, khakis, or professional skirts</li>
                <li>Closed-toe shoes</li>
                <li>Business suits for formal occasions</li>
            </ul>
            
            <p><em>Note: This is draft content. Please contact HR for the complete dress code policy.</em></p>
        ''',
        'code_of_ethics': '''
            <h3>Code of Ethics</h3>
            <p>Our code of ethics guides our decisions and actions in all business matters.</p>
            
            <h3>Core Values</h3>
            <ul>
                <li><strong>Integrity:</strong> Act honestly and ethically in all situations</li>
                <li><strong>Respect:</strong> Value diversity and treat everyone with dignity</li>
                <li><strong>Accountability:</strong> Take responsibility for our actions</li>
                <li><strong>Excellence:</strong> Strive for quality in everything we do</li>
            </ul>
            
            <h3>Ethical Standards</h3>
            <ul>
                <li>Comply with all applicable laws and regulations</li>
                <li>Avoid conflicts of interest</li>
                <li>Protect company and customer information</li>
                <li>Use company resources responsibly</li>
                <li>Report ethical concerns without fear of retaliation</li>
            </ul>
            
            <p><em>Note: This is draft content. Please contact HR for the complete code of ethics.</em></p>
        ''',
        'it_policy': '''
            <h3>IT Usage Policy</h3>
            <p>This policy outlines the acceptable use of company IT resources and systems.</p>
            
            <h3>Acceptable Use</h3>
            <ul>
                <li>Use company devices for business purposes</li>
                <li>Maintain strong passwords and change them regularly</li>
                <li>Keep software and systems up to date</li>
                <li>Report security incidents immediately</li>
                <li>Lock your computer when away from desk</li>
            </ul>
            
            <h3>Security Guidelines</h3>
            <ul>
                <li>Never share passwords or login credentials</li>
                <li>Be cautious with email attachments and links</li>
                <li>Use VPN when accessing company resources remotely</li>
                <li>Encrypt sensitive data</li>
                <li>Follow data backup procedures</li>
            </ul>
            
            <h3>Prohibited Activities</h3>
            <ul>
                <li>Installing unauthorized software</li>
                <li>Accessing inappropriate content</li>
                <li>Sharing confidential information</li>
                <li>Using company resources for personal business</li>
            </ul>
            
            <p><em>Note: This is draft content. Please contact HR for the complete IT policy.</em></p>
        ''',
    }
    
    # Get existing sections from database
    db_sections = HandbookSection.objects.filter(is_active=True).order_by('section_type')
    
    # Create a dictionary of existing sections by section_type
    existing_sections = {section.section_type: section for section in db_sections}
    
    # Build complete sections list with defaults for missing ones
    all_sections = []
    for section_type, title in HandbookSection.SECTION_CHOICES:
        if section_type in existing_sections:
            # Use database content
            all_sections.append(existing_sections[section_type])
        else:
            # Create a temporary object with default content (not saved to DB)
            from types import SimpleNamespace
            default_section = SimpleNamespace(
                section_type=section_type,
                title=dict(HandbookSection.SECTION_CHOICES)[section_type],
                content=DEFAULT_CONTENT.get(section_type, '<p>Content coming soon...</p>'),
                is_active=True
            )
            all_sections.append(default_section)
    
    # Check if user has permission to edit
    can_edit = request.user.has_perm('employee.change_handbooksection') or request.user.is_staff
    
    context = {
        'sections': all_sections,
        'can_edit': can_edit,
    }
    return render(request, 'employee/handbook_dashboard.html', context)


@login_required
@permission_required('employee.change_handbooksection', raise_exception=True)
def edit_handbook_section(request, section_type):
    """
    Edit a handbook section (HR/Admin only)
    """
    section = get_object_or_404(HandbookSection, section_type=section_type)
    
    if request.method == 'POST':
        content = request.POST.get('content', '')
        section.content = content
        section.last_updated_by = request.user
        section.save()
        
        messages.success(request, _('Handbook section updated successfully.'))
        return JsonResponse({'success': True, 'message': _('Section updated successfully')})
    
    return JsonResponse({'success': False, 'message': _('Invalid request')}, status=400)


@login_required
def policy_dashboard(request):
    """
    Display policy sections. HR/Admin can edit, employees can only view.
    """
    # Default demo content for each section
    DEFAULT_CONTENT = {
        'leave_policy': '''
            <h3>Leave Policy Overview</h3>
            <p>Our leave policy is designed to provide employees with adequate time off while maintaining business operations.</p>
            
            <h3>Types of Leave</h3>
            <ul>
                <li><strong>Annual Leave:</strong> 20 days per year (accrued monthly)</li>
                <li><strong>Sick Leave:</strong> 10 days per year</li>
                <li><strong>Casual Leave:</strong> 7 days per year</li>
                <li><strong>Maternity Leave:</strong> As per local labor laws</li>
                <li><strong>Paternity Leave:</strong> 5 days</li>
                <li><strong>Bereavement Leave:</strong> 3 days for immediate family</li>
            </ul>
            
            <h3>Leave Application Process</h3>
            <ul>
                <li>Submit leave requests through the HRMS system</li>
                <li>Apply at least 3 days in advance for planned leave</li>
                <li>Obtain manager approval before taking leave</li>
                <li>For sick leave, notify your manager as soon as possible</li>
                <li>Medical certificate required for sick leave exceeding 3 days</li>
            </ul>
            
            <h3>Leave Balance</h3>
            <p>Unused annual leave may be carried forward to the next year (maximum 5 days). Other leave types do not carry forward.</p>
            
            <p><em>Note: This is draft content. Please contact HR for the complete leave policy.</em></p>
        ''',
        'hr_policy': '''
            <h3>Human Resources Policy</h3>
            <p>Our HR policies ensure fair treatment, professional development, and a positive work environment for all employees.</p>
            
            <h3>Recruitment & Onboarding</h3>
            <ul>
                <li>Equal opportunity employer - merit-based hiring</li>
                <li>Comprehensive onboarding program for new hires</li>
                <li>Probation period: 3-6 months depending on role</li>
                <li>Regular performance reviews during probation</li>
            </ul>
            
            <h3>Performance Management</h3>
            <ul>
                <li>Annual performance reviews</li>
                <li>Quarterly check-ins with managers</li>
                <li>Goal setting and development plans</li>
                <li>360-degree feedback process</li>
            </ul>
            
            <h3>Training & Development</h3>
            <ul>
                <li>Professional development budget for each employee</li>
                <li>Internal training programs and workshops</li>
                <li>Mentorship opportunities</li>
                <li>Support for relevant certifications</li>
            </ul>
            
            <h3>Compensation & Benefits</h3>
            <ul>
                <li>Competitive salary structure</li>
                <li>Annual salary reviews</li>
                <li>Performance-based bonuses</li>
                <li>Health insurance coverage</li>
                <li>Retirement benefits</li>
            </ul>
            
            <p><em>Note: This is draft content. Please contact HR for complete HR policies.</em></p>
        ''',
        'attendance_rules': '''
            <h3>Attendance Rules & Regulations</h3>
            <p>Regular attendance and punctuality are essential for maintaining productivity and team collaboration.</p>
            
            <h3>Working Hours</h3>
            <ul>
                <li>Standard work week: Monday to Friday</li>
                <li>Core hours: 9:00 AM - 6:00 PM (with 1-hour lunch break)</li>
                <li>Flexible working hours available with manager approval</li>
                <li>Total working hours: 40 hours per week</li>
            </ul>
            
            <h3>Clock-In/Clock-Out</h3>
            <ul>
                <li>Use the HRMS system to clock in and out daily</li>
                <li>Clock in at the start of your shift</li>
                <li>Clock out for lunch breaks and at end of shift</li>
                <li>Location tracking enabled for remote work verification</li>
            </ul>
            
            <h3>Punctuality</h3>
            <ul>
                <li>Arrive on time for your scheduled shift</li>
                <li>Late arrivals (after 9:15 AM) must be reported to manager</li>
                <li>Excessive tardiness may result in disciplinary action</li>
                <li>Grace period: 15 minutes per month</li>
            </ul>
            
            <h3>Absences</h3>
            <ul>
                <li>Notify your manager of any absence as early as possible</li>
                <li>Unplanned absences require same-day notification</li>
                <li>Excessive unexcused absences may lead to termination</li>
                <li>Medical documentation required for extended absences</li>
            </ul>
            
            <p><em>Note: This is draft content. Please contact HR for complete attendance rules.</em></p>
        ''',
        'remote_work_policy': '''
            <h3>Remote Work Policy</h3>
            <p>We support flexible work arrangements while maintaining productivity and team collaboration.</p>
            
            <h3>Eligibility</h3>
            <ul>
                <li>Employees who have completed probation period</li>
                <li>Roles suitable for remote work</li>
                <li>Manager approval required</li>
                <li>Demonstrated ability to work independently</li>
            </ul>
            
            <h3>Remote Work Options</h3>
            <ul>
                <li><strong>Hybrid:</strong> 2-3 days remote, 2-3 days in office</li>
                <li><strong>Fully Remote:</strong> Subject to role requirements and approval</li>
                <li><strong>Occasional Remote:</strong> As needed with advance notice</li>
            </ul>
            
            <h3>Requirements</h3>
            <ul>
                <li>Reliable internet connection (minimum 10 Mbps)</li>
                <li>Dedicated workspace free from distractions</li>
                <li>Available during core business hours</li>
                <li>Responsive on company communication channels</li>
                <li>Use company-provided VPN for security</li>
            </ul>
            
            <h3>Attendance Tracking</h3>
            <ul>
                <li>Clock in/out through HRMS system</li>
                <li>Location verification enabled</li>
                <li>Regular check-ins with team and manager</li>
                <li>Maintain same productivity standards as office work</li>
            </ul>
            
            <h3>Equipment & Support</h3>
            <ul>
                <li>Company laptop and necessary peripherals provided</li>
                <li>IT support available during business hours</li>
                <li>Home office allowance (if applicable)</li>
            </ul>
            
            <p><em>Note: This is draft content. Please contact HR for the complete remote work policy.</em></p>
        ''',
        'privacy_terms': '''
            <h3>Privacy Policy & Terms</h3>
            <p>We are committed to protecting the privacy and security of employee and company information.</p>
            
            <h3>Data Collection</h3>
            <ul>
                <li>Personal information collected for employment purposes only</li>
                <li>Performance and attendance data tracked through HRMS</li>
                <li>Location data collected during clock-in/out (with consent)</li>
                <li>Communication data on company systems</li>
            </ul>
            
            <h3>Data Usage</h3>
            <ul>
                <li>HR administration and payroll processing</li>
                <li>Performance management and reviews</li>
                <li>Compliance with legal requirements</li>
                <li>Internal analytics and reporting</li>
            </ul>
            
            <h3>Data Protection</h3>
            <ul>
                <li>All data encrypted and stored securely</li>
                <li>Access restricted to authorized personnel only</li>
                <li>Regular security audits and updates</li>
                <li>Compliance with data protection regulations</li>
            </ul>
            
            <h3>Employee Rights</h3>
            <ul>
                <li>Right to access your personal data</li>
                <li>Right to request corrections to inaccurate data</li>
                <li>Right to data portability</li>
                <li>Right to lodge complaints with supervisory authority</li>
            </ul>
            
            <h3>Confidentiality</h3>
            <ul>
                <li>Employees must maintain confidentiality of company information</li>
                <li>Non-disclosure agreements must be honored</li>
                <li>Sensitive information must not be shared externally</li>
                <li>Data breaches must be reported immediately</li>
            </ul>
            
            <p><em>Note: This is draft content. Please contact HR for the complete privacy policy.</em></p>
        ''',
    }
    
    # Get existing sections from database
    db_sections = PolicySection.objects.filter(is_active=True).order_by('section_type')
    
    # Create a dictionary of existing sections by section_type
    existing_sections = {section.section_type: section for section in db_sections}
    
    # Build complete sections list with defaults for missing ones
    all_sections = []
    for section_type, title in PolicySection.SECTION_CHOICES:
        if section_type in existing_sections:
            # Use database content
            all_sections.append(existing_sections[section_type])
        else:
            # Create a temporary object with default content (not saved to DB)
            from types import SimpleNamespace
            default_section = SimpleNamespace(
                section_type=section_type,
                title=dict(PolicySection.SECTION_CHOICES)[section_type],
                content=DEFAULT_CONTENT.get(section_type, '<p>Content coming soon...</p>'),
                is_active=True
            )
            all_sections.append(default_section)
    
    # Check if user has permission to edit
    can_edit = request.user.has_perm('employee.change_policysection') or request.user.is_staff
    
    context = {
        'sections': all_sections,
        'can_edit': can_edit,
    }
    return render(request, 'employee/policy_dashboard.html', context)


@login_required
@permission_required('employee.change_policysection', raise_exception=True)
def edit_policy_section(request, section_type):
    """
    Edit a policy section (HR/Admin only)
    """
    section = get_object_or_404(PolicySection, section_type=section_type)
    
    if request.method == 'POST':
        content = request.POST.get('content', '')
        section.content = content
        section.last_updated_by = request.user
        section.save()
        
        messages.success(request, _('Policy section updated successfully.'))
        return JsonResponse({'success': True, 'message': _('Section updated successfully')})
    
    return JsonResponse({'success': False, 'message': _('Invalid request')}, status=400)

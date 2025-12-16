"""
Management command to populate Handbook and Policy sections with default content
"""
from django.core.management.base import BaseCommand
from employee.models import HandbookSection, PolicySection


class Command(BaseCommand):
    help = 'Populate Handbook and Policy sections with default content'

    def handle(self, *args, **options):
        self.stdout.write('Populating Handbook sections...')
        
        # Handbook Sections
        handbook_data = [
            {
                'section_type': 'company_rules',
                'title': 'Company Rules & Regulations',
                'content': '''
                    <h3>Welcome to Our Company</h3>
                    <p>These rules and regulations are designed to create a productive and respectful workplace environment.</p>
                    
                    <h3>General Rules</h3>
                    <ul>
                        <li>All employees must maintain professional conduct at all times</li>
                        <li>Punctuality is expected for all scheduled meetings and work hours</li>
                        <li>Respect company property and resources</li>
                        <li>Maintain confidentiality of company information</li>
                    </ul>
                    
                    <h3>Workplace Behavior</h3>
                    <ul>
                        <li>Treat all colleagues with respect and dignity</li>
                        <li>No discrimination or harassment of any kind will be tolerated</li>
                        <li>Maintain a clean and organized workspace</li>
                    </ul>
                '''
            },
            {
                'section_type': 'conduct_guidelines',
                'title': 'Professional Conduct Guidelines',
                'content': '''
                    <h3>Professional Standards</h3>
                    <p>We expect all employees to uphold the highest standards of professional conduct.</p>
                    
                    <h3>Communication</h3>
                    <ul>
                        <li>Communicate clearly and professionally with colleagues and clients</li>
                        <li>Respond to emails and messages in a timely manner</li>
                        <li>Use appropriate language in all business communications</li>
                    </ul>
                    
                    <h3>Teamwork</h3>
                    <ul>
                        <li>Collaborate effectively with team members</li>
                        <li>Share knowledge and support colleagues</li>
                        <li>Participate actively in team meetings and discussions</li>
                    </ul>
                '''
            },
            {
                'section_type': 'dress_code',
                'title': 'Dress Code Policy',
                'content': '''
                    <h3>Dress Code Standards</h3>
                    <p>Our dress code is designed to maintain a professional appearance while allowing comfort.</p>
                    
                    <h3>Business Casual</h3>
                    <ul>
                        <li>Smart casual attire is acceptable for regular office days</li>
                        <li>Business formal attire is required for client meetings</li>
                        <li>Clothing should be clean, neat, and in good condition</li>
                    </ul>
                    
                    <h3>Unacceptable Attire</h3>
                    <ul>
                        <li>Torn or excessively worn clothing</li>
                        <li>Offensive graphics or messages on clothing</li>
                        <li>Overly casual items like flip-flops or athletic wear</li>
                    </ul>
                '''
            },
            {
                'section_type': 'code_of_ethics',
                'title': 'Code of Ethics',
                'content': '''
                    <h3>Our Ethical Standards</h3>
                    <p>We are committed to conducting business with integrity and transparency.</p>
                    
                    <h3>Core Values</h3>
                    <ul>
                        <li><strong>Integrity:</strong> Act honestly and ethically in all situations</li>
                        <li><strong>Respect:</strong> Treat everyone with dignity and respect</li>
                        <li><strong>Accountability:</strong> Take responsibility for your actions</li>
                        <li><strong>Excellence:</strong> Strive for excellence in all endeavors</li>
                    </ul>
                    
                    <h3>Conflict of Interest</h3>
                    <ul>
                        <li>Avoid situations that create conflicts of interest</li>
                        <li>Disclose any potential conflicts to management</li>
                        <li>Do not use company resources for personal gain</li>
                    </ul>
                '''
            },
            {
                'section_type': 'it_policy',
                'title': 'IT Usage Policy',
                'content': '''
                    <h3>Information Technology Guidelines</h3>
                    <p>Proper use of company IT resources is essential for security and productivity.</p>
                    
                    <h3>Acceptable Use</h3>
                    <ul>
                        <li>Company computers and devices are for business purposes</li>
                        <li>Personal use should be minimal and not interfere with work</li>
                        <li>Use strong passwords and change them regularly</li>
                        <li>Do not share login credentials with others</li>
                    </ul>
                    
                    <h3>Security</h3>
                    <ul>
                        <li>Report any security incidents immediately</li>
                        <li>Do not download unauthorized software</li>
                        <li>Be cautious with email attachments and links</li>
                        <li>Lock your computer when away from your desk</li>
                    </ul>
                    
                    <h3>Data Protection</h3>
                    <ul>
                        <li>Protect sensitive company and client information</li>
                        <li>Do not share confidential data externally</li>
                        <li>Follow data backup procedures</li>
                    </ul>
                '''
            },
        ]
        
        for data in handbook_data:
            section, created = HandbookSection.objects.get_or_create(
                section_type=data['section_type'],
                defaults={
                    'title': data['title'],
                    'content': data['content'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {section.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'- Already exists: {section.title}'))
        
        self.stdout.write('\nPopulating Policy sections...')
        
        # Policy Sections
        policy_data = [
            {
                'section_type': 'leave_policy',
                'title': 'Leave Policy',
                'content': '''
                    <h3>Leave Entitlements</h3>
                    <p>Our leave policy is designed to provide work-life balance while maintaining business operations.</p>
                    
                    <h3>Types of Leave</h3>
                    <ul>
                        <li><strong>Annual Leave:</strong> Employees are entitled to paid annual leave</li>
                        <li><strong>Sick Leave:</strong> Paid sick leave for medical reasons</li>
                        <li><strong>Personal Leave:</strong> For personal matters and emergencies</li>
                        <li><strong>Parental Leave:</strong> For new parents</li>
                    </ul>
                    
                    <h3>Leave Application</h3>
                    <ul>
                        <li>Submit leave requests through the HRMS system</li>
                        <li>Provide adequate notice when possible</li>
                        <li>Obtain manager approval before taking leave</li>
                        <li>Medical certificates may be required for sick leave</li>
                    </ul>
                '''
            },
            {
                'section_type': 'hr_policy',
                'title': 'Human Resources Policy',
                'content': '''
                    <h3>HR Policies and Procedures</h3>
                    <p>Our HR policies ensure fair and consistent treatment of all employees.</p>
                    
                    <h3>Recruitment</h3>
                    <ul>
                        <li>Equal opportunity employment practices</li>
                        <li>Merit-based selection process</li>
                        <li>Comprehensive onboarding for new hires</li>
                    </ul>
                    
                    <h3>Performance Management</h3>
                    <ul>
                        <li>Regular performance reviews and feedback</li>
                        <li>Clear goal setting and expectations</li>
                        <li>Professional development opportunities</li>
                    </ul>
                    
                    <h3>Employee Benefits</h3>
                    <ul>
                        <li>Competitive compensation packages</li>
                        <li>Health and wellness programs</li>
                        <li>Retirement savings plans</li>
                    </ul>
                '''
            },
            {
                'section_type': 'attendance_rules',
                'title': 'Attendance Rules & Regulations',
                'content': '''
                    <h3>Attendance Requirements</h3>
                    <p>Regular attendance and punctuality are essential for business success.</p>
                    
                    <h3>Working Hours</h3>
                    <ul>
                        <li>Standard working hours are defined by your employment contract</li>
                        <li>Clock in/out using the HRMS system</li>
                        <li>Breaks should be taken as scheduled</li>
                    </ul>
                    
                    <h3>Tardiness and Absences</h3>
                    <ul>
                        <li>Notify your manager immediately if you will be late or absent</li>
                        <li>Excessive tardiness may result in disciplinary action</li>
                        <li>Unauthorized absences are not permitted</li>
                    </ul>
                    
                    <h3>Time Tracking</h3>
                    <ul>
                        <li>Accurately record all work hours</li>
                        <li>Report any discrepancies to HR</li>
                        <li>Overtime must be pre-approved by management</li>
                    </ul>
                '''
            },
            {
                'section_type': 'remote_work_policy',
                'title': 'Remote Work Policy',
                'content': '''
                    <h3>Remote Work Guidelines</h3>
                    <p>Remote work arrangements must maintain productivity and communication standards.</p>
                    
                    <h3>Eligibility</h3>
                    <ul>
                        <li>Remote work is subject to manager approval</li>
                        <li>Employees must have suitable home office setup</li>
                        <li>Reliable internet connection is required</li>
                    </ul>
                    
                    <h3>Expectations</h3>
                    <ul>
                        <li>Maintain regular working hours</li>
                        <li>Be available for meetings and communications</li>
                        <li>Meet all performance and productivity standards</li>
                        <li>Use company-approved security measures</li>
                    </ul>
                    
                    <h3>Equipment and Security</h3>
                    <ul>
                        <li>Use company-provided equipment when possible</li>
                        <li>Ensure data security and confidentiality</li>
                        <li>Report any technical issues promptly</li>
                    </ul>
                '''
            },
            {
                'section_type': 'privacy_terms',
                'title': 'Privacy Policy & Terms',
                'content': '''
                    <h3>Privacy and Data Protection</h3>
                    <p>We are committed to protecting the privacy and personal information of our employees.</p>
                    
                    <h3>Data Collection</h3>
                    <ul>
                        <li>We collect only necessary personal information</li>
                        <li>Data is used for employment and HR purposes only</li>
                        <li>Information is stored securely and confidentially</li>
                    </ul>
                    
                    <h3>Employee Rights</h3>
                    <ul>
                        <li>Access your personal information upon request</li>
                        <li>Request corrections to inaccurate data</li>
                        <li>Understand how your data is being used</li>
                    </ul>
                    
                    <h3>Confidentiality</h3>
                    <ul>
                        <li>Employee information is kept confidential</li>
                        <li>Data is shared only with authorized personnel</li>
                        <li>We comply with all applicable privacy laws</li>
                    </ul>
                    
                    <h3>Terms of Employment</h3>
                    <ul>
                        <li>Employment is subject to company policies</li>
                        <li>Policies may be updated from time to time</li>
                        <li>Employees will be notified of significant changes</li>
                    </ul>
                '''
            },
        ]
        
        for data in policy_data:
            section, created = PolicySection.objects.get_or_create(
                section_type=data['section_type'],
                defaults={
                    'title': data['title'],
                    'content': data['content'],
                    'is_active': True
                }
            )
            if created:
                self.stdout.write(self.style.SUCCESS(f'✓ Created: {section.title}'))
            else:
                self.stdout.write(self.style.WARNING(f'- Already exists: {section.title}'))
        
        self.stdout.write(self.style.SUCCESS('\n✓ Successfully populated all sections!'))

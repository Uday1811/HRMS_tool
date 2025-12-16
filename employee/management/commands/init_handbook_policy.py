"""
Management command to initialize default handbook and policy content
"""
from django.core.management.base import BaseCommand
from employee.models import HandbookSection, PolicySection


class Command(BaseCommand):
    help = 'Initialize default handbook and policy sections'

    def handle(self, *args, **options):
        self.stdout.write('Initializing handbook sections...')
        
        # Handbook Sections
        handbook_data = {
            'company_rules': {
                'title': 'Company Rules & Regulations',
                'content': '''
                    <h3>Working Hours</h3>
                    <ul>
                        <li>Standard working hours are 9:00 AM to 6:00 PM, Monday to Friday</li>
                        <li>Lunch break is from 1:00 PM to 2:00 PM</li>
                        <li>Flexible working hours may be arranged with manager approval</li>
                        <li>Remote work is permitted up to 2 days per week</li>
                    </ul>
                    
                    <h3>Attendance Policy</h3>
                    <ul>
                        <li>Employees must check in and out using the attendance system</li>
                        <li>Late arrivals (after 9:15 AM) must be reported to HR</li>
                        <li>Excessive tardiness may result in disciplinary action</li>
                        <li>Sick leave requires medical certificate for absences over 2 days</li>
                    </ul>
                '''
            },
            'conduct_guidelines': {
                'title': 'Professional Conduct Guidelines',
                'content': '''
                    <h3>Workplace Behavior</h3>
                    <ul>
                        <li>Treat all colleagues with respect and professionalism</li>
                        <li>Maintain confidentiality of sensitive information</li>
                        <li>Report any harassment or discrimination immediately</li>
                        <li>Avoid conflicts of interest in business dealings</li>
                    </ul>
                    
                    <h3>Meeting Etiquette</h3>
                    <ul>
                        <li>Arrive on time for all scheduled meetings</li>
                        <li>Come prepared with necessary materials and information</li>
                        <li>Mute microphones when not speaking in virtual meetings</li>
                        <li>Respect speaking time and allow others to contribute</li>
                    </ul>
                '''
            },
            'dress_code': {
                'title': 'Dress Code Policy',
                'content': '''
                    <h3>Business Casual (Default)</h3>
                    <ul>
                        <li>Collared shirts, blouses, or sweaters</li>
                        <li>Dress pants, khakis, or knee-length skirts</li>
                        <li>Closed-toe shoes (no flip-flops or sandals)</li>
                        <li>Minimal jewelry and accessories</li>
                    </ul>
                    
                    <h3>Casual Friday</h3>
                    <ul>
                        <li>Jeans in good condition (no rips or tears)</li>
                        <li>Casual shirts, polo shirts, or t-shirts</li>
                        <li>Sneakers or casual shoes acceptable</li>
                        <li>Company branded clothing encouraged</li>
                    </ul>
                '''
            },
            'code_of_ethics': {
                'title': 'Code of Ethics',
                'content': '''
                    <h3>Core Values</h3>
                    <p><strong>Integrity:</strong> Act honestly and transparently in all business dealings</p>
                    <p><strong>Respect:</strong> Value diversity and inclusion in the workplace</p>
                    <p><strong>Excellence:</strong> Strive for quality in everything we do</p>
                    <p><strong>Accountability:</strong> Take responsibility for our actions and decisions</p>
                '''
            },
            'it_policy': {
                'title': 'IT Usage Policy',
                'content': '''
                    <h3>Computer & Internet</h3>
                    <ul>
                        <li>Company computers are for business use primarily</li>
                        <li>Limited personal use is permitted during breaks</li>
                        <li>Do not install unauthorized software</li>
                        <li>Report security incidents immediately to IT</li>
                    </ul>
                    
                    <h3>Password Security</h3>
                    <ul>
                        <li>Use strong passwords with at least 8 characters</li>
                        <li>Include uppercase, lowercase, numbers, and symbols</li>
                        <li>Change passwords every 90 days</li>
                        <li>Never share passwords with colleagues</li>
                    </ul>
                '''
            },
        }

        for section_type, data in handbook_data.items():
            HandbookSection.objects.get_or_create(
                section_type=section_type,
                defaults=data
            )
            self.stdout.write(self.style.SUCCESS(f'Created/Updated: {data["title"]}'))

        self.stdout.write('\nInitializing policy sections...')
        
        # Policy Sections
        policy_data = {
            'leave_policy': {
                'title': 'Leave Policy',
                'content': '''
                    <h3>Annual Leave</h3>
                    <ul>
                        <li>All full-time employees are entitled to 25 days of annual leave per year</li>
                        <li>Part-time employees receive pro-rated leave based on working hours</li>
                        <li>Leave accrues at 2.08 days per month of service</li>
                        <li>Maximum carry-over of 5 days to the following year</li>
                    </ul>
                    
                    <h3>Sick Leave</h3>
                    <ul>
                        <li>12 days of sick leave per calendar year</li>
                        <li>Medical certificate required for absences over 2 consecutive days</li>
                        <li>Unused sick leave does not carry over to the next year</li>
                        <li>Family care leave available for immediate family members</li>
                    </ul>
                '''
            },
            'hr_policy': {
                'title': 'Human Resources Policy',
                'content': '''
                    <h3>Equal Opportunity</h3>
                    <p>We are committed to providing equal employment opportunities to all employees and applicants regardless of race, color, religion, gender, sexual orientation, age, national origin, disability, or veteran status.</p>
                    
                    <h3>Anti-Harassment</h3>
                    <ul>
                        <li>Zero tolerance for harassment, discrimination, or bullying</li>
                        <li>All complaints will be investigated promptly and confidentially</li>
                        <li>Retaliation against complainants is strictly prohibited</li>
                    </ul>
                '''
            },
            'attendance_rules': {
                'title': 'Attendance Rules & Regulations',
                'content': '''
                    <h3>Working Hours</h3>
                    <ul>
                        <li>Standard working hours: 9:00 AM - 6:00 PM</li>
                        <li>Core hours: 10:00 AM - 4:00 PM</li>
                        <li>Flexible start time between 8:00 AM - 10:00 AM</li>
                        <li>40 hours per week minimum requirement</li>
                    </ul>
                    
                    <h3>Punctuality</h3>
                    <ul>
                        <li>Grace period of 15 minutes for late arrival</li>
                        <li>3 late arrivals in a month triggers counseling</li>
                        <li>Excessive tardiness may result in disciplinary action</li>
                        <li>Early departure requires manager approval</li>
                    </ul>
                '''
            },
            'remote_work_policy': {
                'title': 'Remote Work Policy',
                'content': '''
                    <h3>Eligibility</h3>
                    <ul>
                        <li>Employees with at least 6 months of service</li>
                        <li>Satisfactory performance rating in last review</li>
                        <li>Role suitable for remote work</li>
                        <li>Manager approval required</li>
                    </ul>
                    
                    <h3>Guidelines</h3>
                    <ul>
                        <li>Maximum 2 days per week remote work</li>
                        <li>Must maintain same working hours as office days</li>
                        <li>Reliable internet connection required</li>
                        <li>Available for video calls during core hours</li>
                    </ul>
                '''
            },
            'privacy_terms': {
                'title': 'Privacy Policy & Terms',
                'content': '''
                    <h3>Data Privacy</h3>
                    <ul>
                        <li>GDPR compliant data handling</li>
                        <li>Data used for legitimate business purposes only</li>
                        <li>Strict data retention limits</li>
                    </ul>
                    
                    <h3>Confidentiality</h3>
                    <ul>
                        <li>NDA required for all employees</li>
                        <li>No unauthorized sharing of company information</li>
                        <li>Trade secrets protection</li>
                    </ul>
                    
                    <h3>Intellectual Property Rights</h3>
                    <ul>
                        <li>Work created belongs to the company</li>
                        <li>Inventions must be assigned to company</li>
                        <li>Disclose any conflicts of interest</li>
                    </ul>
                '''
            },
        }

        for section_type, data in policy_data.items():
            PolicySection.objects.get_or_create(
                section_type=section_type,
                defaults=data
            )
            self.stdout.write(self.style.SUCCESS(f'Created/Updated: {data["title"]}'))

        self.stdout.write(self.style.SUCCESS('\n✓ All sections initialized successfully!'))

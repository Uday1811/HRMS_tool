# Project Structure

## Root Directory Layout

```
horilla/
├── horilla/                    # Main Django project configuration
├── base/                       # Core base functionality and shared utilities
├── employee/                   # Employee management module
├── recruitment/                # Recruitment and hiring workflows
├── attendance/                 # Time tracking and attendance
├── leave/                      # Leave management system
├── payroll/                    # Payroll processing
├── pms/                        # Performance Management System
├── onboarding/                 # Employee onboarding processes
├── offboarding/                # Employee exit processes
├── asset/                      # Asset management and tracking
├── helpdesk/                   # Internal support system
├── project/                    # Project management module
├── notifications/              # Notification system
├── horilla_*/                  # Additional Horilla modules
├── templates/                  # Global Django templates
├── static/                     # Global static files
├── media/                      # User-uploaded files
├── load_data/                  # Initial data fixtures
└── manage.py                   # Django management script
```

## Django App Structure

Each Django app follows a consistent structure:

```
app_name/
├── admin.py                    # Django admin configuration
├── apps.py                     # App configuration
├── models.py                   # Database models
├── views.py                    # View functions/classes
├── urls.py                     # URL routing
├── forms.py                    # Django forms
├── filters.py                  # Django-filter configurations
├── signals.py                  # Django signals
├── tests.py                    # Unit tests
├── migrations/                 # Database migrations
├── templates/                  # App-specific templates
├── static/                     # App-specific static files
├── templatetags/               # Custom template tags
└── methods/                    # Utility functions (some apps)
```

## Core Modules

### Base Module (`base/`)
- Foundation functionality shared across all apps
- User authentication and authorization
- Company and department models
- Common utilities and decorators
- Context processors and middleware

### Employee Module (`employee/`)
- Employee profile management
- Personal information and work details
- Employee hierarchy and reporting structure
- Employee dashboard and analytics

### Horilla Extensions (`horilla_*/`)
- **horilla_api/** - REST API endpoints
- **horilla_audit/** - System audit logging
- **horilla_views/** - Generic view utilities
- **horilla_widgets/** - Custom form widgets
- **horilla_crumbs/** - Breadcrumb navigation
- **horilla_documents/** - Document management
- **horilla_automations/** - Workflow automation
- **horilla_backup/** - Backup management
- **horilla_ldap/** - LDAP integration

## Configuration Files

- **horilla/settings.py** - Main Django settings
- **horilla/horilla_apps.py** - App registration and configuration
- **horilla/urls.py** - Root URL configuration
- **.env** - Environment variables (from .env.dist template)
- **requirements.txt** - Python dependencies
- **package.json** - Node.js dependencies
- **docker-compose.yaml** - Docker configuration

## Static Assets Organization

```
static/
├── css/                        # Stylesheets
├── js/                         # JavaScript files
├── images/                     # Images and icons
└── fonts/                      # Font files
```

## Template Structure

```
templates/
├── base.html                   # Base template
├── auth/                       # Authentication templates
├── registration/               # User registration templates
└── [app_name]/                 # App-specific templates
```

## Naming Conventions

- **Models**: PascalCase (e.g., `Employee`, `AttendanceRecord`)
- **Views**: snake_case functions or PascalCase classes
- **URLs**: kebab-case with underscores for namespaces
- **Templates**: snake_case with app prefix
- **Static files**: kebab-case organization

## Module Dependencies

- All apps depend on `base/` for core functionality
- `employee/` is a dependency for most HR-related modules
- `notifications/` provides system-wide notification capabilities
- `horilla_audit/` tracks changes across all modules

## Development Guidelines

- Each app should be self-contained with minimal cross-dependencies
- Use the `base/` module for shared utilities and models
- Follow Django's MVT (Model-View-Template) pattern
- Implement proper permission checks using Django's auth system
- Use Django's built-in features (admin, forms, etc.) where possible
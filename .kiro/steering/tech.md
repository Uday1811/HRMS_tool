# Technology Stack

## Backend Framework
- **Django 4.2.23** - Primary web framework
- **Python 3.x** - Programming language
- **Django REST Framework** - API development
- **PostgreSQL** - Primary database (SQLite for development)

## Frontend Technologies
- **Bootstrap** - CSS framework
- **jQuery** - JavaScript library
- **Alpine.js** - Lightweight JavaScript framework
- **Chart.js** - Data visualization
- **Select2** - Enhanced select boxes
- **HTML5/CSS3** - Standard web technologies

## Key Dependencies
- **django-environ** - Environment variable management
- **django-filter** - Filtering capabilities
- **django-import-export** - Data import/export
- **django-simple-history** - Model history tracking
- **django-auditlog** - Audit logging
- **APScheduler** - Task scheduling
- **Pillow** - Image processing
- **ReportLab** - PDF generation
- **openpyxl** - Excel file handling
- **gunicorn** - WSGI server for production
- **whitenoise** - Static file serving

## Development Tools
- **Laravel Mix** - Asset compilation (via npm)
- **Docker** - Containerization support
- **Pre-commit hooks** - Code quality enforcement

## Common Commands

### Development Setup
```bash
# Create virtual environment
python3 -m venv horillavenv
source horillavenv/bin/activate  # Linux/Mac
# or
.\horillavenv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Environment setup
mv .env.dist .env
# Edit .env file with your configuration
```

### Database Operations
```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser
python manage.py createsuperuser

# Load demo data (optional)
python manage.py loaddata load_data/*.json
```

### Development Server
```bash
# Run development server
python manage.py runserver
# or on custom port
python manage.py runserver 8080
```

### Internationalization
```bash
# Compile translations
python manage.py compilemessages

# Generate translation files
python manage.py makemessages --all
```

### Frontend Assets
```bash
# Install npm dependencies
npm install

# Build assets for development
npm run development
```

### Docker Deployment
```bash
# Build and run with Docker Compose
docker-compose up --build

# Run in background
docker-compose up -d
```

## Environment Configuration
- Use `.env` file for environment-specific settings
- PostgreSQL recommended for production
- SQLite acceptable for development
- Support for cloud storage (GCP) via environment variables
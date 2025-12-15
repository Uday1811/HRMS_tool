#!/usr/bin/env python
"""
Quick setup script for Employee Attendance Dashboard
Run this after installing the new dashboard files
"""

import os
import sys

def main():
    print("=" * 60)
    print("Employee Attendance Dashboard - Setup")
    print("=" * 60)
    print()
    
    print("Step 1: Running migrations...")
    print("-" * 60)
    print("Command: python manage.py makemigrations")
    print("Command: python manage.py migrate")
    print()
    
    print("Step 2: Collecting static files (if needed)...")
    print("-" * 60)
    print("Command: python manage.py collectstatic --noinput")
    print()
    
    print("Step 3: Access the dashboard...")
    print("-" * 60)
    print("URL: http://localhost:8000/attendance/employee-dashboard/")
    print()
    
    print("Step 4: Test the features...")
    print("-" * 60)
    print("✓ Clock In/Out with location tracking")
    print("✓ Live timer display")
    print("✓ Monthly statistics")
    print("✓ Attendance logs")
    print()
    
    print("=" * 60)
    print("Setup instructions displayed!")
    print("=" * 60)
    print()
    print("Next steps:")
    print("1. Run the migration commands above")
    print("2. Start your Django server: python manage.py runserver")
    print("3. Navigate to the employee dashboard URL")
    print("4. Test clock-in functionality")
    print()
    print("For detailed documentation, see:")
    print("attendance/EMPLOYEE_DASHBOARD_README.md")
    print()

if __name__ == "__main__":
    main()

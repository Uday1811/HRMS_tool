"""
admin.py
"""

from django.contrib import admin

from horilla_audit.models import AuditTag, PetabytzAuditInfo, PetabytzAuditLog

# Register your models here.

admin.site.register(AuditTag)

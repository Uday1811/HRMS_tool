"""
Models for Company Handbook and Policy Management
"""
from django.db import models
from django.utils.translation import gettext_lazy as _
from base.horilla_company_manager import PetabytzCompanyManager
from base.models import PetabytzModel


class HandbookSection(PetabytzModel):
    """
    Model to store editable handbook sections
    """
    SECTION_CHOICES = [
        ('company_rules', _('Company Rules & Regulations')),
        ('conduct_guidelines', _('Professional Conduct Guidelines')),
        ('dress_code', _('Dress Code Policy')),
        ('code_of_ethics', _('Code of Ethics')),
        ('it_policy', _('IT Usage Policy')),
    ]
    
    section_type = models.CharField(max_length=50, choices=SECTION_CHOICES, unique=True)
    title = models.CharField(max_length=200)
    content = models.TextField(help_text=_("HTML content for the section"))
    is_active = models.BooleanField(default=True)
    last_updated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='handbook_updates'
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = PetabytzCompanyManager()
    
    class Meta:
        verbose_name = _('Handbook Section')
        verbose_name_plural = _('Handbook Sections')
        ordering = ['section_type']
    
    def __str__(self):
        return f"{self.get_section_type_display()}"


class PolicySection(PetabytzModel):
    """
    Model to store editable policy sections
    """
    SECTION_CHOICES = [
        ('leave_policy', _('Leave Policy')),
        ('hr_policy', _('Human Resources Policy')),
        ('attendance_rules', _('Attendance Rules & Regulations')),
        ('remote_work_policy', _('Remote Work Policy')),
        ('privacy_terms', _('Privacy Policy & Terms')),
    ]
    
    section_type = models.CharField(max_length=50, choices=SECTION_CHOICES, unique=True)
    title = models.CharField(max_length=200)
    content = models.TextField(help_text=_("HTML content for the section"))
    is_active = models.BooleanField(default=True)
    last_updated_by = models.ForeignKey(
        'auth.User',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='policy_updates'
    )
    updated_at = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    objects = PetabytzCompanyManager()
    
    class Meta:
        verbose_name = _('Policy Section')
        verbose_name_plural = _('Policy Sections')
        ordering = ['section_type']
    
    def __str__(self):
        return f"{self.get_section_type_display()}"

"""
horilla_company_manager.py
"""

import logging
from typing import Coroutine, Sequence

from django.db import models
from django.db.models.query import QuerySet

from horilla.horilla_middlewares import _thread_locals
from horilla.signals import post_bulk_update, pre_bulk_update

logger = logging.getLogger(__name__)
django_filter_update = QuerySet.update


def update(self, *args, **kwargs):
    # pre_update signal
    request = getattr(_thread_locals, "request", None)
    self.request = request
    pre_bulk_update.send(sender=self.model, queryset=self, args=args, kwargs=kwargs)
    result = django_filter_update(self, *args, **kwargs)
    # post_update signal
    post_bulk_update.send(sender=self.model, queryset=self, args=args, kwargs=kwargs)

    return result


setattr(QuerySet, "update", update)


class PetabytzCompanyManager(models.Manager):
    """
    PetabytzCompanyManager
    """

    def __init__(self, related_company_field=None, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.related_company_field = related_company_field
        self.check_fields = [
            "employee_id",
            "requested_employee_id",
        ]

    def get_queryset(self):
        """
        get_queryset method with strict multi-tenant isolation
        """
        queryset = super().get_queryset()
        
        # Get company_id from thread locals (set by CompanyIsolationMiddleware)
        # This is the most reliable source for the current request's context
        company_id = getattr(_thread_locals, "company_id", None)
        
        # Fallback to request session if available and thread local is missing
        if not company_id:
            request = getattr(_thread_locals, "request", None)
            if request:
                company_id = request.session.get("company_id")
                # Also check 'selected_company' as used by CompanyMiddleware
                if not company_id:
                    selected = request.session.get("selected_company")
                    if selected and selected != "all":
                        company_id = selected

        if company_id:
            try:
                # 0. Support existing related_company_field initialization
                if self.related_company_field:
                    kwargs = {self.related_company_field: company_id}
                    queryset = queryset.filter(**kwargs)

                # 1. Prefer explicit model-defined filter method
                elif hasattr(self.model, 'get_company_filter'):
                    q_filter = self.model.get_company_filter(company_id)
                    if q_filter:
                        queryset = queryset.filter(q_filter)
                
                # 2. Fallback to direct company_id field if it exists
                # Note: We check field existence by name in fields
                elif 'company_id' in [f.name for f in self.model._meta.fields]:
                     queryset = queryset.filter(company_id=company_id)
                     
                # 3. Fallback for Employee model specifically (known structure)
                elif self.model.__name__ == 'Employee' and hasattr(self.model, 'employee_work_info'):
                    queryset = queryset.filter(employee_work_info__company_id=company_id)
                    
            except Exception as e:
                logger.error(f"Error applying company isolation filter on {self.model.__name__}: {e}")

        # Original duplicate check logic
        try:
            has_duplicates = queryset.count() != queryset.distinct().count()
            if has_duplicates:
                queryset = queryset.distinct()
        except:
            pass
            
        return queryset

    def all(self):
        """
        Override the all() method
        """
        queryset = []
        try:
            queryset = self.get_queryset()
            if queryset.exists():
                try:
                    model_name = queryset.model._meta.model_name
                    if model_name == "employee":
                        request = getattr(_thread_locals, "request", None)
                        if not getattr(request, "is_filtering", None):
                            queryset = queryset.filter(is_active=True)
                    else:
                        for field in queryset.model._meta.fields:
                            if isinstance(field, models.ForeignKey):
                                if field.name in self.check_fields:
                                    related_model_is_active_filter = {
                                        f"{field.name}__is_active": True
                                    }
                                    queryset = queryset.filter(
                                        **related_model_is_active_filter
                                    )
                except:
                    pass
        except:
            pass
        return queryset

    def filter(self, *args, **kwargs):
        queryset = super().filter(*args, **kwargs)
        setattr(_thread_locals, "queryset_filter", queryset)
        return queryset

    def entire(self):
        """
        Fetch all datas from a model without applying any company filter.
        """
        queryset = super().get_queryset()
        return queryset  # No filtering applied

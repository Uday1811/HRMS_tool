"""
Views for login tracking functionality
"""
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Q
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.generic import ListView
from django.contrib import messages
from django.http import JsonResponse
from django.template.loader import render_to_string

from .login_tracking_models import UserLoginLog


def is_admin_or_hr(user):
    """Check if user is admin or has HR permissions"""
    return user.is_superuser or user.groups.filter(name__in=['HR', 'Admin']).exists()


@login_required
@user_passes_test(is_admin_or_hr)
def login_logs_view(request):
    """View to display login/logout logs"""
    
    # Get filter parameters
    action_filter = request.GET.get('action', '')
    user_filter = request.GET.get('user', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Base queryset
    logs = UserLoginLog.objects.select_related('user').all()
    
    # Apply filters
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    if user_filter:
        logs = logs.filter(
            Q(user__username__icontains=user_filter) |
            Q(user__first_name__icontains=user_filter) |
            Q(user__last_name__icontains=user_filter) |
            Q(user__email__icontains=user_filter)
        )
    
    if date_from:
        logs = logs.filter(timestamp__date__gte=date_from)
    
    if date_to:
        logs = logs.filter(timestamp__date__lte=date_to)
    
    # Pagination
    paginator = Paginator(logs, 25)  # Show 25 logs per page
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    
    context = {
        'page_obj': page_obj,
        'logs': page_obj,
        'action_filter': action_filter,
        'user_filter': user_filter,
        'date_from': date_from,
        'date_to': date_to,
        'total_logs': logs.count(),
    }
    
    return render(request, 'base/login_logs.html', context)


@login_required
@user_passes_test(is_admin_or_hr)
def login_logs_ajax(request):
    """AJAX view for login logs table"""
    
    # Get filter parameters
    action_filter = request.GET.get('action', '')
    user_filter = request.GET.get('user', '')
    date_from = request.GET.get('date_from', '')
    date_to = request.GET.get('date_to', '')
    
    # Base queryset
    logs = UserLoginLog.objects.select_related('user').all()
    
    # Apply filters
    if action_filter:
        logs = logs.filter(action=action_filter)
    
    if user_filter:
        logs = logs.filter(
            Q(user__username__icontains=user_filter) |
            Q(user__first_name__icontains=user_filter) |
            Q(user__last_name__icontains=user_filter) |
            Q(user__email__icontains=user_filter)
        )
    
    if date_from:
        logs = logs.filter(timestamp__date__gte=date_from)
    
    if date_to:
        logs = logs.filter(timestamp__date__lte=date_to)
    
    # Pagination
    paginator = Paginator(logs, 25)
    page_number = request.GET.get('page', 1)
    page_obj = paginator.get_page(page_number)
    
    # Render table rows
    html = render_to_string('base/login_logs_table.html', {
        'logs': page_obj,
        'page_obj': page_obj,
    })
    
    return JsonResponse({
        'html': html,
        'has_next': page_obj.has_next(),
        'has_previous': page_obj.has_previous(),
        'page_number': page_obj.number,
        'total_pages': paginator.num_pages,
        'total_logs': logs.count(),
    })


@method_decorator(login_required, name='dispatch')
@method_decorator(user_passes_test(is_admin_or_hr), name='dispatch')
class LoginLogListView(ListView):
    """Class-based view for login logs"""
    
    model = UserLoginLog
    template_name = 'base/login_logs_list.html'
    context_object_name = 'logs'
    paginate_by = 25
    ordering = ['-timestamp']
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Apply filters
        action_filter = self.request.GET.get('action')
        if action_filter:
            queryset = queryset.filter(action=action_filter)
        
        user_filter = self.request.GET.get('user')
        if user_filter:
            queryset = queryset.filter(
                Q(user__username__icontains=user_filter) |
                Q(user__first_name__icontains=user_filter) |
                Q(user__last_name__icontains=user_filter) |
                Q(user__email__icontains=user_filter)
            )
        
        date_from = self.request.GET.get('date_from')
        if date_from:
            queryset = queryset.filter(timestamp__date__gte=date_from)
        
        date_to = self.request.GET.get('date_to')
        if date_to:
            queryset = queryset.filter(timestamp__date__lte=date_to)
        
        return queryset.select_related('user')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'action_filter': self.request.GET.get('action', ''),
            'user_filter': self.request.GET.get('user', ''),
            'date_from': self.request.GET.get('date_from', ''),
            'date_to': self.request.GET.get('date_to', ''),
            'total_logs': self.get_queryset().count(),
        })
        return context
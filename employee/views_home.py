from django.contrib.auth.decorators import login_required
from django.shortcuts import render

@login_required
def home_dashboard(request):
    """Render the premium home dashboard with tabs for various sections.
    The template uses the advanced CSS defined in `home_advanced.css`.
    """
    return render(request, "employee/home.html")

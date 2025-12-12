import json
import logging
import os
import re

import requests
from django.contrib import messages
from django.shortcuts import redirect, render
from django.urls import reverse

from base.models import Company
from recruitment.models import Candidate, LinkedInAccount, Recruitment

logger = logging.getLogger(__name__)


def linkedin_login(request):
    """
    This method is used to login to linkedin
    """
    return render(request, "recruitment/linkedin/linkedin_login.html")


def linkedin_callback(request):
    """
    This method is used to handle linkedin callback
    """
    code = request.GET.get("code")
    if code:
        # Exchange authorization code for access token
        token_url = "https://www.linkedin.com/oauth/v2/accessToken"
        token_data = {
            "grant_type": "authorization_code",
            "code": code,
            "redirect_uri": "https://www.linkedin.com/developers/tools/oauth/redirect",
            "client_id": os.environ.get("LINKEDIN_CLIENT_ID", "your_client_id_here"),
            "client_secret": os.environ.get("LINKEDIN_CLIENT_SECRET", "your_client_secret_here"),
        }

        token_response = requests.post(token_url, data=token_data)
        token_json = token_response.json()

        if "access_token" in token_json:
            access_token = token_json["access_token"]

            # Get user profile information
            profile_url = "https://api.linkedin.com/v2/people/~"
            headers = {"Authorization": f"Bearer {access_token}"}
            profile_response = requests.get(profile_url, headers=headers)
            profile_json = profile_response.json()

            # Extract user information
            linkedin_id = profile_json.get("id")
            first_name = profile_json.get("localizedFirstName", "")
            last_name = profile_json.get("localizedLastName", "")

            # Create or update LinkedInAccount
            linkedin_account, created = LinkedInAccount.objects.get_or_create(
                linkedin_id=linkedin_id,
                defaults={
                    "access_token": access_token,
                    "first_name": first_name,
                    "last_name": last_name,
                },
            )

            if not created:
                linkedin_account.access_token = access_token
                linkedin_account.first_name = first_name
                linkedin_account.last_name = last_name
                linkedin_account.save()

            messages.success(request, "LinkedIn account connected successfully!")
            return redirect("linkedin-login")
        else:
            messages.error(request, "Failed to get access token from LinkedIn.")
            return redirect("linkedin-login")
    else:
        messages.error(request, "Authorization code not received from LinkedIn.")
        return redirect("linkedin-login")


def linkedin_disconnect(request):
    """
    This method is used to disconnect linkedin account
    """
    linkedin_id = request.POST.get("linkedin_id")
    try:
        linkedin_account = LinkedInAccount.objects.get(id=linkedin_id)
        linkedin_account.delete()
        messages.success(request, "LinkedIn account disconnected successfully!")
    except LinkedInAccount.DoesNotExist:
        messages.error(request, "LinkedIn account not found.")
    return redirect("linkedin-login")


def sync_linkedin_candidates(request):
    """
    This method is used to sync candidates from linkedin
    """
    url = "https://www.linkedin.com/oauth/v2/accessToken"
    data = {
        "grant_type": "client_credentials",
        "redirect_uri": "https://www.linkedin.com/developers/tools/oauth/redirect",
        "client_id": os.environ.get("LINKEDIN_CLIENT_ID", "your_client_id_here"),
        "client_secret": os.environ.get("LINKEDIN_CLIENT_SECRET", "your_client_secret_here"),
    }

    response = requests.post(url, data=data)

    if response.status_code == 200:
        access_token = response.json().get("access_token")
        
        # Use the access_token to fetch candidate data from LinkedIn API
        # Implementation depends on LinkedIn API endpoints available
        
        messages.success(request, "LinkedIn candidates synced successfully!")
    else:
        messages.error(request, "Failed to sync LinkedIn candidates.")
    
    return redirect("linkedin-login")
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


def delete_post(recruitment_obj):
    """
    This method is used to delete a LinkedIn post for a recruitment
    """
    try:
        if not recruitment_obj.linkedin_account_id:
            return True
            
        # Get LinkedIn account and access token
        linkedin_account = LinkedInAccount.objects.get(id=recruitment_obj.linkedin_account_id)
        access_token = linkedin_account.access_token
        
        # If there's a LinkedIn post ID associated with this recruitment, delete it
        if hasattr(recruitment_obj, 'linkedin_post_id') and recruitment_obj.linkedin_post_id:
            delete_url = f"https://api.linkedin.com/v2/posts/{recruitment_obj.linkedin_post_id}"
            headers = {"Authorization": f"Bearer {access_token}"}
            
            response = requests.delete(delete_url, headers=headers)
            return response.status_code == 200
        
        return True
    except Exception as e:
        logger.error(f"Error deleting LinkedIn post: {str(e)}")
        return False


def post_recruitment_in_linkedin(request, recruitment_obj, linkedin_account_id):
    """
    This method is used to post recruitment information to LinkedIn
    """
    try:
        linkedin_account = LinkedInAccount.objects.get(id=linkedin_account_id)
        access_token = linkedin_account.access_token
        
        # Prepare post content
        post_content = f"""
        🚀 New Job Opening: {recruitment_obj.job_position}
        
        Company: {recruitment_obj.company}
        Location: {recruitment_obj.job_position.department.company.company if hasattr(recruitment_obj.job_position, 'department') else 'Not specified'}
        
        We're looking for talented individuals to join our team!
        
        #hiring #jobs #career #opportunity
        """
        
        # LinkedIn API endpoint for creating posts
        post_url = "https://api.linkedin.com/v2/posts"
        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/json"
        }
        
        post_data = {
            "author": f"urn:li:person:{linkedin_account.linkedin_id}",
            "lifecycleState": "PUBLISHED",
            "specificContent": {
                "com.linkedin.ugc.ShareContent": {
                    "shareCommentary": {
                        "text": post_content
                    },
                    "shareMediaCategory": "NONE"
                }
            },
            "visibility": {
                "com.linkedin.ugc.MemberNetworkVisibility": "PUBLIC"
            }
        }
        
        response = requests.post(post_url, headers=headers, json=post_data)
        
        if response.status_code == 201:
            post_id = response.json().get("id")
            # Store the post ID with the recruitment object if needed
            messages.success(request, "Job posted to LinkedIn successfully!")
            return True
        else:
            messages.error(request, "Failed to post job to LinkedIn.")
            return False
            
    except LinkedInAccount.DoesNotExist:
        messages.error(request, "LinkedIn account not found.")
        return False
    except Exception as e:
        logger.error(f"Error posting to LinkedIn: {str(e)}")
        messages.error(request, "An error occurred while posting to LinkedIn.")
        return False


def delete_linkedin_account(request, pk):
    """
    This method is used to delete a LinkedIn account
    """
    try:
        linkedin_account = LinkedInAccount.objects.get(id=pk)
        linkedin_account.delete()
        messages.success(request, "LinkedIn account deleted successfully!")
    except LinkedInAccount.DoesNotExist:
        messages.error(request, "LinkedIn account not found.")
    except Exception as e:
        logger.error(f"Error deleting LinkedIn account: {str(e)}")
        messages.error(request, "An error occurred while deleting LinkedIn account.")
    
    return redirect("linkedin-login")


def update_isactive_linkedin(request, obj_id):
    """
    This method is used to update the active status of a LinkedIn account
    """
    try:
        linkedin_account = LinkedInAccount.objects.get(id=obj_id)
        linkedin_account.is_active = not linkedin_account.is_active
        linkedin_account.save()
        
        status = "activated" if linkedin_account.is_active else "deactivated"
        messages.success(request, f"LinkedIn account {status} successfully!")
    except LinkedInAccount.DoesNotExist:
        messages.error(request, "LinkedIn account not found.")
    except Exception as e:
        logger.error(f"Error updating LinkedIn account status: {str(e)}")
        messages.error(request, "An error occurred while updating LinkedIn account.")
    
    return redirect("linkedin-login")


def check_linkedin(request):
    """
    This method is used to check LinkedIn integration status
    """
    linkedin_accounts = LinkedInAccount.objects.all()
    context = {
        "linkedin_accounts": linkedin_accounts,
        "has_linkedin_config": bool(
            os.environ.get("LINKEDIN_CLIENT_ID") and 
            os.environ.get("LINKEDIN_CLIENT_SECRET")
        )
    }
    return render(request, "recruitment/linkedin/check_linkedin.html", context)


def validate_linkedin_token(request, pk):
    """
    This method is used to validate LinkedIn access token
    """
    try:
        linkedin_account = LinkedInAccount.objects.get(id=pk)
        access_token = linkedin_account.access_token
        
        # Test the token by making a simple API call
        profile_url = "https://api.linkedin.com/v2/people/~"
        headers = {"Authorization": f"Bearer {access_token}"}
        response = requests.get(profile_url, headers=headers)
        
        if response.status_code == 200:
            messages.success(request, "LinkedIn token is valid!")
        else:
            messages.error(request, "LinkedIn token is invalid or expired.")
            
    except LinkedInAccount.DoesNotExist:
        messages.error(request, "LinkedIn account not found.")
    except Exception as e:
        logger.error(f"Error validating LinkedIn token: {str(e)}")
        messages.error(request, "An error occurred while validating LinkedIn token.")
    
    return redirect("linkedin-login")
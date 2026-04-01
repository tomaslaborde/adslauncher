"""
src/config/settings.py
Handles loading of Environment Variables and SDK initialization.
"""

import os
from dotenv import load_dotenv
from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.adaccount import AdAccount

def init_meta_api():
    """Initializes the Meta Graph API session."""
    load_dotenv()

    app_id = os.getenv("META_APP_ID")
    app_secret = os.getenv("META_APP_SECRET")
    access_token = os.getenv("META_ACCESS_TOKEN")

    if not all([app_id, app_secret, access_token]):
        print("⚠️ Missing Meta Developer Credentials in .env!")
        print("Please configureMETA_APP_ID, META_APP_SECRET, and META_ACCESS_TOKEN.")
        return False

    try:
        FacebookAdsApi.init(app_id, app_secret, access_token)
        return True
    except Exception as e:
        print(f"Error initializing Meta API: {e}")
        return False

def get_ad_account():
    """Returns the configured AdAccount object."""
    account_id = os.getenv("META_AD_ACCOUNT_ID")
    if not account_id:
        raise ValueError("META_AD_ACCOUNT_ID is not set in .env")
    
    # Prefix with 'act_' if not already present
    if not account_id.startswith('act_'):
        account_id = f"act_{account_id}"
        
    return AdAccount(account_id)

def get_page_id():
    """Returns the Facebook Page ID for associating ads."""
    page_id = os.getenv("META_PAGE_ID")
    if not page_id:
        raise ValueError("META_PAGE_ID is not set in .env")
    return page_id

def reinit_with_page_token():
    """Re-initializes the Meta API session using the Page Access Token for creative creation."""
    app_id = os.getenv("META_APP_ID")
    app_secret = os.getenv("META_APP_SECRET")
    page_token = os.getenv("META_PAGE_ACCESS_TOKEN")
    if not page_token:
        raise ValueError("META_PAGE_ACCESS_TOKEN is not set in .env")
    FacebookAdsApi.init(app_id, app_secret, page_token)

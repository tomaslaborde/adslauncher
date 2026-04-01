"""
src/services/campaign_service.py
Handles the creation and management of live Meta Ad Campaigns.
"""

from facebook_business.adobjects.campaign import Campaign

def create_campaign(account, name="Claude Code Automated Campaign", objective="OUTCOME_TRAFFIC"):
    """
    Creates a new Campaign in the specified Ad Account.
    """
    params = {
        Campaign.Field.name: name,
        Campaign.Field.objective: objective,
        Campaign.Field.status: Campaign.Status.paused,  # Always start paused for safety
        Campaign.Field.special_ad_categories: ['NONE'], # Required by API v7.0+
        'is_adset_budget_sharing_enabled': False,
    }

    print(f"🚀 Pushing Live Campaign '{name}' to Meta API...")
    
    # Executes the live POST call to the Graph API
    campaign = account.create_campaign(params=params)
    
    return campaign

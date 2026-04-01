"""
src/services/adset_service.py
Handles creation and definition of Ad Sets (Budgets, Audiences, Placement) directly to Meta.
"""

from facebook_business.adobjects.adset import AdSet

def create_adset(account, campaign_id, name="Broad US Targeting - Claude", daily_budget=5000,
                 genders=None, interests=None, platforms=None):
    """
    Creates an Ad Set belonging to a specific Campaign.
    """
    if genders is None:
        genders = [1, 2]  # All
    if platforms is None:
        platforms = ['facebook', 'instagram']

    targeting = {
        'geo_locations': {
            'countries': ['US']
        },
        'age_min': 18,
        'age_max': 65,
        'genders': genders,
        'publisher_platforms': platforms,
        'device_platforms': ['mobile', 'desktop'],
        'targeting_automation': {'advantage_audience': 0}
    }

    if interests:
        targeting['flexible_spec'] = [
            {'interests': interests}
        ]

    params = {
        AdSet.Field.name: name,
        AdSet.Field.campaign_id: campaign_id,
        AdSet.Field.daily_budget: daily_budget,
        AdSet.Field.billing_event: 'IMPRESSIONS',
        AdSet.Field.optimization_goal: 'REACH',
        AdSet.Field.bid_amount: 100,
        AdSet.Field.targeting: targeting,
        AdSet.Field.status: AdSet.Status.paused,
    }

    print(f"🎯 Pushing Live Ad Set '{name}' to Meta API...")
    
    # Live execution POST block
    adset = account.create_ad_set(params=params)
    
    return adset

"""
src/services/search_service.py
Handles searching the live Meta Graph API for targeting options (like Interest IDs).
"""

from facebook_business.api import FacebookAdsApi
from facebook_business.adobjects.targetingsearch import TargetingSearch

def search_ad_interests(query):
    """
    Searches Meta's live database for ad interests matching the query string.
    """
    print(f"🔍 Searching live Meta Graph API for interest: '{query}'...")
    
    results = TargetingSearch.search(params={
        'type': 'adinterest',
        'q': query,
    })
    
    # Returning parsed dictionaries for easier consumption
    parsed_results = []
    for match in results:
        parsed_results.append({
            'id': match['id'],
            'name': match['name'],
            'audience_size': match.get('audience_size_lower_bound', 0)
        })
        
    return parsed_results

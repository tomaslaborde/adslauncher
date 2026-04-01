"""
src/main.py
Entry point for the Meta Ads Publisher Script.
Runs a completely automated live pipeline from local files to a published Meta Ad.
"""

import sys
import os
import csv

# Ensure the src directory is in the Python path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.config.settings import init_meta_api, get_ad_account, get_page_id, reinit_with_page_token
from src.services.campaign_service import create_campaign
from src.services.search_service import search_ad_interests
from src.services.adset_service import create_adset
from src.services.creative_service import upload_ad_image, create_ad_creative, create_final_ad

def main():
    print("🤖 Claude Code Automated Meta Ads Publisher (LIVE MODE)...\n")

    # Step 1: Init API
    if not init_meta_api():
        print("FATAL: Failed to init Meta API. Please check your .env credentials.")
        return

    account = get_ad_account()
    page_id = get_page_id()
    
    # Pre-Flight: Parse the CSV Ad Copy
    print("------------------------------------------------------------------")
    csv_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'creates', 'ad_copy.csv')
    print(f"📖 Parsing Ad Copy from: {csv_file}")
    
    with open(csv_file, mode='r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        first_row = next(reader) # Grab just the first variation for this demo
        ad_headline = first_row['Headline']
        ad_description = first_row['Description']
        
    print(f"Selected Headline: '{ad_headline}'")
    
    # Pre-Flight: Upload specific Image Asset
    image_file = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'Creatives', 'image.png')
    live_image_hash = upload_ad_image(account, image_file)

    print("------------------------------------------------------------------")
    # Step 2: Reuse existing Campaign
    from facebook_business.adobjects.campaign import Campaign
    campaign_id = "120244919737170745"
    campaign = Campaign(campaign_id)
    print(f"♻️ Reusing existing Campaign ID: {campaign_id}\n")

    # Step 3: Reuse existing Ad Set
    from facebook_business.adobjects.adset import AdSet
    adset_id = "120244919909560745"
    adset = AdSet(adset_id)
    print(f"♻️ Reusing existing Ad Set ID: {adset_id}\n")

    # Step 4: Create Creative & Final Ad (using Page Access Token)
    print("🔑 Switching to Page Access Token for creative creation...")
    reinit_with_page_token()

    creative = create_ad_creative(
        account, 
        page_id=page_id, 
        image_hash=live_image_hash,
        title=ad_headline, 
        message=ad_description
    )
    print(f"✅ Created Live Creative ID: {creative.get_id()}\n")
    
    # Final step
    create_final_ad(account, adset_id=adset_id, creative_id=creative.get_id(), name="Summer 2026")

    print("\n🎉 Live Publishing Pipeline Complete!")

if __name__ == "__main__":
    main()

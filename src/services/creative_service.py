"""
src/services/creative_service.py
Handles the live heavy lifting of constructing ad content (Image Uploads, Text, URL) directly to Meta.
"""

from facebook_business.adobjects.adimage import AdImage
from facebook_business.adobjects.adcreative import AdCreative
from facebook_business.adobjects.ad import Ad

def upload_ad_image(account, image_path):
    """
    Uploads a local image file to the Meta Ad Account's Asset Library.
    Returns the image hash.
    """
    print(f"🖼️ Uploading raw image {image_path} to Meta API...")
    
    image = AdImage(parent_id=account.get_id())
    image[AdImage.Field.filename] = image_path
    
    image.remote_create()
    
    print(f"✅ Image Uploaded! Hash: {image[AdImage.Field.hash]}")
    return image[AdImage.Field.hash]


def create_ad_creative(account, page_id, image_hash, title="Try Claude Code!", message="Automate your marketing today."):
    """
    Creates a live Ad Creative object representing the visual/text aspect of an Ad.
    """
    print(f"🖌️ Pushing Live Ad Creative...")

    params = {
        AdCreative.Field.name: f"Creative: {title}",
        AdCreative.Field.object_story_spec: {
            'page_id': page_id,
            'link_data': {
                'image_hash': image_hash,
                'link': 'https://example.com/automation',
                'message': message,
                'name': title,
                'call_to_action': {
                    'type': 'LEARN_MORE',
                }
            }
        }
    }

    # Execute POST
    creative = account.create_ad_creative(params=params)
    
    return creative


def create_final_ad(account, adset_id, creative_id, name="Live Automated Ad 01"):
    """
    Ties the Ad Set and the Ad Creative together into a final published Ad.
    """
    print(f"🚀 Publishing Final Live Ad '{name}'...")
    
    params = {
        Ad.Field.name: name,
        Ad.Field.adset_id: adset_id,
        Ad.Field.creative: {'creative_id': creative_id},
        Ad.Field.status: Ad.Status.paused,
    }

    # Execute POST
    ad = account.create_ad(params=params)
    
    print(f"✅ Live Ad Published Successfully! ID: {ad.get_id()}")
    return ad

# backend/services/photos_service.py
import requests
from ..config import config
import random

def get_destination_photos(destination: str, count: int = 5):
    """
    Get destination photos from Pexels and Unsplash with fallback.
    
    Args:
        destination: Destination name
        count: Number of photos to fetch
    
    Returns:
        List of photo URLs
    """
    photos = []
    
    # Try Pexels first
    try:
        pexels_key = config.PEXELS_API_KEY
        if pexels_key and pexels_key.strip():
            url = "https://api.pexels.com/v1/search"
            headers = {"Authorization": pexels_key}
            params = {
                "query": f"{destination} travel tourism",
                "per_page": count,
                "orientation": "landscape"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=5)
            if response.ok:
                data = response.json()
                for photo in data.get("photos", [])[:count]:
                    photos.append({
                        "url": photo["src"]["large"],
                        "photographer": photo["photographer"],
                        "source": "pexels",
                        "alt": f"{destination} - Photo by {photo['photographer']}"
                    })
                
                if photos:
                    return photos
    except Exception as e:
        print(f"Pexels API failed: {e}")
    
    # Try Unsplash as fallback
    try:
        unsplash_key = config.UNSPLASH_ACCESS_KEY
        if unsplash_key and unsplash_key.strip():
            url = "https://api.unsplash.com/search/photos"
            headers = {"Authorization": f"Client-ID {unsplash_key}"}
            params = {
                "query": f"{destination} travel",
                "per_page": count,
                "orientation": "landscape"
            }
            
            response = requests.get(url, headers=headers, params=params, timeout=5)
            if response.ok:
                data = response.json()
                for photo in data.get("results", [])[:count]:
                    photos.append({
                        "url": photo["urls"]["regular"],
                        "photographer": photo["user"]["name"],
                        "source": "unsplash",
                        "alt": f"{destination} - Photo by {photo['user']['name']}"
                    })
                
                if photos:
                    return photos
    except Exception as e:
        print(f"Unsplash API failed: {e}")
    
    # Fallback to placeholder images
    placeholder_photos = [
        {
            "url": f"https://source.unsplash.com/800x600/?{destination.replace(' ', '-')},travel,{i}",
            "photographer": "Unsplash",
            "source": "placeholder",
            "alt": f"{destination} travel photo"
        }
        for i in range(1, count + 1)
    ]
    
    return placeholder_photos


def get_hero_image(destination: str):
    """
    Get a single hero image for destination.
    
    Args:
        destination: Destination name
    
    Returns:
        Photo URL or None
    """
    photos = get_destination_photos(destination, count=1)
    return photos[0]["url"] if photos else None

import os
import requests
from dotenv import load_dotenv

load_dotenv()
OPENTRIP_API_KEY = os.getenv("OPENTRIP_API_KEY")

def get_city_coords(city):
    """Get latitude and longitude of a city"""
    url = "https://api.opentripmap.com/0.1/en/places/geoname"
    params = {"name": city, "apikey": OPENTRIP_API_KEY}
    res = requests.get(url, params=params)
    if res.status_code == 200:
        data = res.json()
        return data.get("lat"), data.get("lon")
    return None, None

def fetch_place_details(xid):
    """Get detailed info about a place"""
    url = f"https://api.opentripmap.com/0.1/en/places/xid/{xid}"
    params = {"apikey": OPENTRIP_API_KEY}
    res = requests.get(url, params=params)
    if res.status_code == 200:
        return res.json()
    return {}

def search_hotels(city, radius=5000, limit=10):
    """Search hotels & resorts in a city"""
    lat, lon = get_city_coords(city)
    if not lat:
        return []
    url = "https://api.opentripmap.com/0.1/en/places/radius"
    params = {
        "radius": radius,
        "lon": lon,
        "lat": lat,
        "kinds": "other_hotels",
        "limit": limit,
        "apikey": OPENTRIP_API_KEY
    }
    res = requests.get(url, params=params)
    results = []
    if res.status_code == 200:
        for place in res.json().get("features", []):
            xid = place["properties"].get("xid")
            details = fetch_place_details(xid)
            results.append(details)
    return results

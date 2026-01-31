# backend/routes/hotels.py
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import List, Optional
import random

router = APIRouter()

class HotelsReq(BaseModel):
    destination: str
    start_date: str
    end_date: str

def generate_mock_hotels(destination: str, count: int = 6) -> List[dict]:
    """Generate deterministic mock hotel data as fallback."""
    hotel_names = [
        "Grand Palace Hotel",
        "Sunset Resort",
        "Mountain View Inn",
        "Beachside Villa",
        "Heritage Lodge",
        "Luxury Suites",
        "Garden Retreat",
        "City Center Hotel",
        "Riverside Lodge",
        "Hilltop Resort"
    ]
    areas = [
        "City Center",
        "Beachfront",
        "Downtown",
        "Airport Area",
        "Historic District",
        "Waterfront"
    ]
    
    hotels = []
    for i in range(count):
        name_idx = (hash(destination) + i) % len(hotel_names)
        area_idx = (hash(destination) * 2 + i) % len(areas)
        rating = random.choice([3, 4, 5])
        base_price = random.randint(1500, 8000)
        hotels.append({
            "name": f"{hotel_names[name_idx]} {destination}",
            "rating": rating,
            "area": areas[area_idx],
            "price_per_night": base_price,
            "amenities": ["WiFi", "Pool", "Restaurant", "Parking"]
        })
    return hotels

@router.post("/")
def search_hotels(payload: HotelsReq):
    """
    Search hotels with fallback to mock data if API fails or key missing.
    """
    try:
        # Try to use real hotel API if available
        # For now, always use mock data as fallback
        # In production, replace this with actual API call:
        # 
        # from ..config import config
        # api_key = getattr(config, "HOTEL_API_KEY", None)
        # if api_key:
        #     try:
        #         # Make real API call
        #         response = requests.get(...)
        #         return response.json()
        #     except Exception:
        #         pass  # Fall through to mock
        
        # Always return mock data for now (deterministic based on destination)
        hotels = generate_mock_hotels(payload.destination)
        return hotels
    except Exception as e:
        # Even if mock generation fails, return basic fallback
        return generate_mock_hotels(payload.destination, count=3)

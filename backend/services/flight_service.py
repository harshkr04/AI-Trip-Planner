import random
import requests
from ..config import config
from datetime import datetime

def get_flight_options(trip: dict):
    destination = trip.get("destination", "Unknown")
    start_date = trip.get("start_date", "2025-11-01")
    
    # Check for Amadeus keys
    api_key = config.AMADEUS_API_KEY
    api_secret = config.AMADEUS_API_SECRET
    
    if api_key and api_secret:
        try:
            # 1. Get Access Token
            token_url = f"{config.AMADEUS_BASE_URL}/v1/security/oauth2/token"
            token_resp = requests.post(token_url, data={
                "grant_type": "client_credentials",
                "client_id": api_key,
                "client_secret": api_secret
            }, timeout=5)
            
            if token_resp.status_code == 200:
                access_token = token_resp.json().get("access_token")
                
                # 2. Search Flights (Simplified: DEL -> Destination)
                # We need IATA code for destination. For now, let's try a simple mapping or city search.
                # Since city search is complex, we might skip it for this demo and just check if we can get a code.
                # For robustness, if we can't easily get IATA, we might fallback.
                # BUT, let's try to be "real" if possible.
                # Let's assume the destination is a city name.
                
                # Search for City IATA
                headers = {"Authorization": f"Bearer {access_token}"}
                city_url = f"{config.AMADEUS_BASE_URL}/v1/reference-data/locations"
                city_params = {"subType": "CITY", "keyword": destination, "page[limit]": 1}
                city_resp = requests.get(city_url, headers=headers, params=city_params, timeout=5)
                
                dest_code = None
                if city_resp.status_code == 200 and city_resp.json().get("data"):
                    dest_code = city_resp.json()["data"][0]["iataCode"]
                
                if dest_code:
                    flight_url = f"{config.AMADEUS_BASE_URL}/v2/shopping/flight-offers"
                    flight_params = {
                        "originLocationCode": "DEL", # Assume Delhi for now
                        "destinationLocationCode": dest_code,
                        "departureDate": start_date,
                        "adults": 1,
                        "max": 3
                    }
                    flight_resp = requests.get(flight_url, headers=headers, params=flight_params, timeout=8)
                    
                    if flight_resp.status_code == 200:
                        offers = flight_resp.json().get("data", [])
                        real_flights = []
                        for offer in offers:
                            itineraries = offer.get("itineraries", [])
                            if not itineraries: continue
                            segments = itineraries[0].get("segments", [])
                            if not segments: continue
                            
                            first_seg = segments[0]
                            last_seg = segments[-1]
                            carrier = first_seg.get("carrierCode", "Unknown") # We'd need a carrier map, but code is ok
                            price = offer.get("price", {}).get("total", "0")
                            currency = offer.get("price", {}).get("currency", "EUR")
                            
                            # Simple formatting
                            real_flights.append({
                                "airline": f"Airline {carrier}", # Placeholder for carrier name lookup
                                "from": "DEL",
                                "to": dest_code,
                                "depart": first_seg.get("departure", {}).get("at", "").replace("T", " "),
                                "price": f"{price} {currency}",
                                "duration": itineraries[0].get("duration", "")[2:] # Strip PT
                            })
                        
                        if real_flights:
                            return {"live": True, "options": real_flights}
                            
        except Exception as e:
            print(f"Amadeus API failed: {e}")
            # Fall through to mock

    # Mock Fallback
    base_prices = {
        "Goa": 4500, "Mumbai": 3500, "Bangalore": 4000, "Chennai": 4500,
        "Jaipur": 3000, "Udaipur": 3500, "Manali": 5000, "Kerala": 5500,
        "Kolkata": 4000, "Hyderabad": 3500, "default": 4000
    }
    base_price = base_prices.get(destination, base_prices["default"])
    airlines = [("IndiGo", 0.9), ("Air India", 1.1), ("SpiceJet", 0.85), ("Vistara", 1.2)]
    flights = []
    times = ["06:00 AM", "09:30 AM", "02:15 PM", "06:45 PM"]
    for i, (airline, multiplier) in enumerate(airlines):
        price_variation = random.uniform(0.8, 1.2)
        final_price = int(base_price * multiplier * price_variation)
        flights.append({
            "airline": airline,
            "from": "Delhi",
            "to": destination,
            "depart": f"{start_date} {times[i]}",
            "price": f"₹{final_price}",
            "duration": "2h 30m"
        })
    flights.sort(key=lambda x: int(x["price"].replace("₹", "").replace(" ", "")))
    
    return {
        "live": False, 
        "options": flights, 
        "fallback_reason": "No API key or API limit" if not api_key else "API Error/No routes"
    }

import requests
import json

url = "http://localhost:8000/api/itinerary/generate"
payload = {
    "prompt": "Plan a 4-day beach trip to Goa starting from Delhi with good food and nightlife",
    "start_date": "2025-11-26",
    "end_date": "2025-11-29"
}

try:
    print("Sending request to:", url)
    print("Payload:", json.dumps(payload, indent=2))
    
    response = requests.post(url, json=payload, timeout=120)
    
    print(f"\nStatus Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"\nResponse Body:")
    print(json.dumps(response.json(), indent=2))
    
except requests.exceptions.Timeout:
    print("ERROR: Request timed out after 120 seconds")
except requests.exceptions.ConnectionError as e:
    print(f"ERROR: Connection error - {e}")
except Exception as e:
    print(f"ERROR: {type(e).__name__}: {e}")
    if hasattr(e, 'response'):
        print(f"Response text: {e.response.text}")

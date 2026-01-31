# backend/services/serper_service.py
import requests
from ..config import config

def search_destination_info(destination: str, query_type: str = "search"):
    """
    Search for destination information using Serper API (Google Search).
    
    Args:
        destination: Destination name
        query_type: Type of search - "search", "images", "news"
    
    Returns:
        Search results
    """
    try:
        api_key = config.SERPER_API_KEY
        if not api_key or not api_key.strip():
            return {"error": "Serper API key not configured"}
        
        url = f"https://google.serper.dev/{query_type}"
        headers = {
            "X-API-KEY": api_key.strip(),
            "Content-Type": "application/json"
        }
        
        payload = {
            "q": f"{destination} travel guide tourism",
            "num": 5
        }
        
        response = requests.post(url, json=payload, headers=headers, timeout=5)
        
        if response.ok:
            return response.json()
        else:
            return {"error": f"API returned status {response.status_code}"}
            
    except Exception as e:
        print(f"Serper API failed: {e}")
        return {"error": str(e)}


def get_destination_highlights(destination: str):
    """
    Get top highlights and attractions for a destination.
    
    Args:
        destination: Destination name
    
    Returns:
        List of highlights
    """
    results = search_destination_info(destination, "search")
    
    if "error" in results:
        return []
    
    highlights = []
    for result in results.get("organic", [])[:5]:
        highlights.append({
            "title": result.get("title", ""),
            "snippet": result.get("snippet", ""),
            "link": result.get("link", ""),
            "source": "serper"
        })
    
    return highlights

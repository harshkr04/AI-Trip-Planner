# backend/routes/location.py
from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Optional
import requests
from ..config import config

router = APIRouter()

def get_mock_location_data(location: str) -> dict:
    """Generate mock location data as fallback."""
    return {
        "summary": f"{location} is a beautiful destination known for its scenic beauty, rich culture, and vibrant atmosphere. Whether you're seeking adventure, relaxation, or cultural experiences, {location} offers something for every traveler.",
        "youtube_videos": [
            {
                "title": f"Top 10 Things to Do in {location}",
                "videoId": "dQw4w9WgXcQ",
                "thumbnail": "https://img.youtube.com/vi/dQw4w9WgXcQ/mqdefault.jpg"
            },
            {
                "title": f"{location} Travel Guide 2025",
                "videoId": "jNQXAC9IVRw",
                "thumbnail": "https://img.youtube.com/vi/jNQXAC9IVRw/mqdefault.jpg"
            },
            {
                "title": f"Best Places to Visit in {location}",
                "videoId": "9bZkp7q19f0",
                "thumbnail": "https://img.youtube.com/vi/9bZkp7q19f0/mqdefault.jpg"
            }
        ],
        "activities": [
            {"title": "City Tour", "type": "Sightseeing", "duration": "3-4 hours"},
            {"title": "Local Market Visit", "type": "Shopping", "duration": "2 hours"},
            {"title": "Mountain Trekking", "type": "Adventure", "duration": "Full day"},
            {"title": "Beach Activities", "type": "Recreation", "duration": "Half day"},
            {"title": "Cultural Museum", "type": "Culture", "duration": "2-3 hours"},
            {"title": "Sunset Viewpoint", "type": "Sightseeing", "duration": "1 hour"}
        ],
        "news_articles": [
            {
                "title": f"Latest Travel Updates for {location}",
                "description": f"Stay updated with the latest travel information and tips for visiting {location}.",
                "url": "https://example.com/news1",
                "source": "Travel News",
                "publishedAt": "2025-01-15T10:00:00Z"
            },
            {
                "title": f"{location} Tourism on the Rise",
                "description": f"Tourism in {location} has seen significant growth this year.",
                "url": "https://example.com/news2",
                "source": "Tourism Weekly",
                "publishedAt": "2025-01-10T14:30:00Z"
            }
        ]
    }

@router.get("/details")
def get_location_details(location: str = Query(..., min_length=1)):
    """
    Aggregator endpoint that returns location summary, YouTube videos, activities, and news.
    Falls back to mock data if APIs/keys are missing.
    """
    try:
        result = {
            "location": location,
            "summary": "",
            "youtube_videos": [],
            "activities": [],
            "news_articles": []
        }
        
        # Try to get Wikipedia summary (optional, can fail gracefully)
        try:
            wiki_url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{location.replace(' ', '_')}"
            wiki_resp = requests.get(wiki_url, timeout=3)
            if wiki_resp.status_code == 200:
                wiki_data = wiki_resp.json()
                result["summary"] = wiki_data.get("extract", "")
        except Exception:
            pass  # Fall through to mock
        
        # Try YouTube API if key available
        youtube_key = getattr(config, "YOUTUBE_API_KEY", None)
        if youtube_key:
            try:
                yt_url = "https://www.googleapis.com/youtube/v3/search"
                yt_params = {
                    "part": "snippet",
                    "q": f"{location} travel guide",
                    "type": "video",
                    "maxResults": 5,
                    "key": youtube_key
                }
                yt_resp = requests.get(yt_url, params=yt_params, timeout=5)
                if yt_resp.status_code == 200:
                    yt_data = yt_resp.json()
                    result["youtube_videos"] = [
                        {
                            "title": item["snippet"]["title"],
                            "videoId": item["id"]["videoId"],
                            "thumbnail": item["snippet"]["thumbnails"]["medium"]["url"]
                        }
                        for item in yt_data.get("items", [])
                    ]
            except Exception:
                pass  # Fall through to mock
        
        # Try news API
        news_key = getattr(config, "NEWSAPI_KEY", None)
        if news_key:
            try:
                news_url = "https://newsapi.org/v2/everything"
                news_params = {
                    "q": f"{location} travel",
                    "pageSize": 5,
                    "language": "en",
                    "sortBy": "publishedAt",
                    "apiKey": news_key
                }
                news_resp = requests.get(news_url, params=news_params, timeout=5)
                if news_resp.status_code == 200:
                    news_data = news_resp.json()
                    result["news_articles"] = news_data.get("articles", [])
            except Exception:
                pass  # Fall through to mock
        
        # Fill in missing data with mock
        mock_data = get_mock_location_data(location)
        if not result["summary"]:
            result["summary"] = mock_data["summary"]
        if not result["youtube_videos"]:
            result["youtube_videos"] = mock_data["youtube_videos"]
        if not result["activities"]:
            result["activities"] = mock_data["activities"]
        if not result["news_articles"]:
            result["news_articles"] = mock_data["news_articles"]
        
        return result
    except Exception as e:
        # Ultimate fallback: return all mock data
        return get_mock_location_data(location)


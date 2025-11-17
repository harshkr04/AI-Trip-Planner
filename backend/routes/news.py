# backend/routes/news.py
from fastapi import APIRouter, HTTPException, Query
import requests
from ..config import config

router = APIRouter()

@router.get("/")
def get_news(q: str = Query("travel", min_length=1), page_size: int = 10):
    key = getattr(config, "NEWSAPI_KEY", None)
    if not key:
        # return mock articles when key not present
        items = []
        for i in range(page_size):
            items.append({
                "title": f"Sample travel article about {q} #{i+1}",
                "description": f"Sample description for {q} article {i+1}.",
                "url": "https://example.com",
                "source": {"name": "MockNews"},
                "publishedAt": "2025-01-01T00:00:00Z",
                "author": "AI Demo"
            })
        return {"status": "ok", "totalResults": len(items), "articles": items}

    url = "https://newsapi.org/v2/everything"
    params = {
        "q": q,
        "pageSize": page_size,
        "language": "en",
        "sortBy": "publishedAt",
        "apiKey": key
    }
    try:
        r = requests.get(url, params=params, timeout=8)
        r.raise_for_status()
        return r.json()
    except requests.RequestException as e:
        raise HTTPException(status_code=502, detail=str(e))

# backend/routes/history.py
# Alias for sessions delete endpoint
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import os, json

router = APIRouter()

# Path for session store (same as sessions.py)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # backend/
DB_FILE = os.path.join(BASE_DIR, "ai_sessions.json")

def load_sessions():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_sessions(arr):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(arr, f, indent=2, ensure_ascii=False)

@router.delete("/{history_id}")
def delete_history(history_id: str):
    """Delete history item by ID. Uses same storage as sessions."""
    sessions = load_sessions()
    new = [s for s in sessions if str(s.get("id")) != str(history_id)]
    if len(new) == len(sessions):
        raise HTTPException(status_code=404, detail="History item not found")
    save_sessions(new)
    return JSONResponse({"status": "ok", "deleted": history_id})


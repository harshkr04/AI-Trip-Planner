# backend/routes/sessions.py
from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import os, json
from typing import List

router = APIRouter()

# Path for a small file-based session store (keep in repo; replace with DB in prod)
BASE_DIR = os.path.dirname(os.path.dirname(__file__))  # backend/
DB_FILE = os.path.join(BASE_DIR, "ai_sessions.json")

# ensure file exists
if not os.path.exists(DB_FILE):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump([], f)

def load_sessions():
    try:
        with open(DB_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_sessions(arr):
    with open(DB_FILE, "w", encoding="utf-8") as f:
        json.dump(arr, f, indent=2, ensure_ascii=False)

@router.get("/", response_model=List[dict])
def list_sessions():
    return load_sessions()

@router.post("/")
def save_session(session: dict):
    """Save or update a session."""
    sessions = load_sessions()
    session_id = str(session.get("id", ""))
    # Remove existing if present
    sessions = [s for s in sessions if str(s.get("id")) != session_id]
    # Add new one at the front
    sessions.insert(0, session)
    # Keep only last 50
    sessions = sessions[:50]
    save_sessions(sessions)
    return JSONResponse({"status": "ok", "saved": session_id})

@router.delete("/{session_id}")
def delete_session(session_id: str):
    """Delete a session by ID. Also available at /api/history/{id}."""
    sessions = load_sessions()
    new = [s for s in sessions if str(s.get("id")) != str(session_id)]
    if len(new) == len(sessions):
        # nothing removed -> not found
        raise HTTPException(status_code=404, detail="Session not found")
    save_sessions(new)
    return JSONResponse({"status": "ok", "deleted": session_id})

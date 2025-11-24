# backend/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .config import config
from .routes import sessions as sessions_route
import importlib
import os
import sys
import traceback

# Try to import your config object; fall back to defaults if import fails.
try:
    from .config import config
except Exception:
    # If the import failed, print reason to terminal for debugging, but continue with defaults.
    print("Warning: failed to import backend.config — using fallback defaults.")
    traceback.print_exc()
    class _DefaultConfig:
        APP_NAME = "AI Trip Planner (dev)"
        FRONTEND_ORIGIN = "http://localhost:3000"
        # Add any other config keys you expect to use (placeholders)
        WEATHER_API_KEY = ""
        NEWSAPI_KEY = ""
    config = _DefaultConfig()

app = FastAPI(title=getattr(config, "APP_NAME", "AI Trip Planner"))

# Startup event to check DB persistence
from .database import SessionLocal
from .models import User

@app.on_event("startup")
def startup_db_check():
    db = SessionLocal()
    try:
        count = db.query(User).count()
        print(f"----------------------------------------------------------------")
        print(f"[STARTUP] Database persistence check: Found {count} users in DB.")
        print(f"----------------------------------------------------------------")
    except Exception as e:
        print(f"[STARTUP] Error checking DB: {e}")
    finally:
        db.close()

# Configure CORS
frontend_origin = getattr(config, "FRONTEND_ORIGIN", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://localhost:3001",
        "http://localhost:3002",
        "http://localhost:3003",
        "http://localhost:3005",
        "http://127.0.0.1:3000",
        "http://127.0.0.1:3001"
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(sessions_route.router, prefix="/api/sessions", tags=["sessions"])

# Helper to import and include routers only when available.
def try_include_router(module_name: str, prefix: str, tag: str):
    """
    Attempts to import module_name (full dotted path) and include its 'router' into app.
    Any import errors are printed but won't stop the app from starting.
    """
    try:
        mod = importlib.import_module(module_name)
        if hasattr(mod, "router"):
            app.include_router(mod.router, prefix=prefix, tags=[tag])
            print(f"Included router: {module_name} -> {prefix}")
        else:
            print(f"Module {module_name} has no attribute 'router' — skipped.")
    except Exception as e:
        print(f"Could not include router {module_name}: {e}")
        # print traceback for debugging
        traceback.print_exc()

# List of (module, prefix, tag). Use the package path 'backend.routes.*' because uvicorn runs from project root.
routers_to_try = [
    ("backend.routes.itinerary", "/api/itinerary", "itinerary"),
    ("backend.routes.pdf", "/api/pdf", "pdf"),
    ("backend.routes.news", "/api/news", "news"),
    ("backend.routes.flights", "/api/flights", "flights"),
    ("backend.routes.hotels", "/api/hotels", "hotels"),
    ("backend.routes.sessions", "/api/sessions", "sessions"),
    ("backend.routes.history", "/api/history", "history"),
    ("backend.routes.location", "/api/location", "location"),
    ("backend.routes.auth", "/api/auth", "auth"),
]

for mod_name, prefix, tag in routers_to_try:
    try_include_router(mod_name, prefix, tag)

# ============================================================================
# EMERGENCY AUTH FIX - Direct endpoints to make auth work immediately
# ============================================================================
from fastapi import HTTPException, Depends
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr
from passlib.context import CryptContext
from .database import get_db
from datetime import datetime, timedelta
from jose import jwt

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

class RegisterRequest(BaseModel):
    email: EmailStr
    password: str
    name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)

@app.post("/api/auth/register", status_code=201)
def emergency_register(payload: RegisterRequest, db: Session = Depends(get_db)):
    try:
        existing = db.query(User).filter(User.email == payload.email).first()
        if existing:
            raise HTTPException(status_code=409, detail="Email already registered")
        
        hashed_pw = pwd_context.hash(payload.password)
        new_user = User(
            email=payload.email,
            name=payload.name,
            hashed_password=hashed_pw,
            picture=""
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"[AUTH] Registration successful: {new_user.email}")
        
        token = create_access_token({"sub": new_user.email, "id": new_user.id})
        return {
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "name": new_user.name,
                "picture": new_user.picture
            },
            "token": token
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[AUTH] Registration error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create account")

@app.post("/api/auth/login")
def emergency_login(payload: LoginRequest, db: Session = Depends(get_db)):
    try:
        user = db.query(User).filter(User.email == payload.email).first()
        if not user or not user.hashed_password:
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        if not pwd_context.verify(payload.password, user.hashed_password):
            raise HTTPException(status_code=401, detail="Invalid email or password")
        
        print(f"[AUTH] Login successful: {user.email}")
        
        token = create_access_token({"sub": user.email, "id": user.id})
        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "picture": user.picture
            },
            "token": token
        }
    except HTTPException:
        raise
    except Exception as e:
        print(f"[AUTH] Login error: {e}")
        raise HTTPException(status_code=500, detail="Login failed")

# ============================================================================

@app.get("/")
def read_root():
    return {"message": f"{getattr(config, 'APP_NAME', 'AI Trip Planner')} is running"}

# optional: convenient health check
@app.get("/health")
def health():
    return {"status": "ok"}

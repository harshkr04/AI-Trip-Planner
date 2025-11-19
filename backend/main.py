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

# Configure CORS
frontend_origin = getattr(config, "FRONTEND_ORIGIN", "http://localhost:3000")
app.add_middleware(
    CORSMiddleware,
    allow_origins=[frontend_origin],
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
]

for mod_name, prefix, tag in routers_to_try:
    try_include_router(mod_name, prefix, tag)

@app.get("/")
def read_root():
    return {"message": f"{getattr(config, 'APP_NAME', 'AI Trip Planner')} is running"}

# optional: convenient health check
@app.get("/health")
def health():
    return {"status": "ok"}

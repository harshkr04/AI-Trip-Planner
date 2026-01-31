import os
from dotenv import load_dotenv

# Load .env once at import time
load_dotenv()

class Config:
    # Core
    APP_NAME = "AI Trip Planner API"
    ENV = os.getenv("ENV", "dev")

    # CORS
    FRONTEND_ORIGIN = os.getenv("FRONTEND_ORIGIN", "http://localhost:3000")

    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "sqlite:///./sql_app.db")

    # LLM (Groq)
    GROQ_API_KEY = os.getenv("GROQ_API_KEY")
    GROQ_MODEL = os.getenv("GROQ_MODEL", "llama-3-70b-8192")
    LLM_TEMPERATURE = float(os.getenv("LLM_TEMPERATURE", "0.7"))

    # External APIs
    WEATHER_API_KEY = os.getenv("WEATHER_API_KEY")       # e.g. OpenWeather
    RAPIDAPI_KEY = os.getenv("RAPIDAPI_KEY")             # for flights/hotels

    # Feature flags
    USE_MOCK = os.getenv("USE_MOCK", "false").lower() == "true"  # Changed default to false
    
    # Amadeus (Flights)
    AMADEUS_API_KEY: str = os.getenv("AMADEUS_API_KEY", "")
    AMADEUS_API_SECRET: str = os.getenv("AMADEUS_API_SECRET", "")
    AMADEUS_BASE_URL: str = os.getenv("AMADEUS_BASE_URL", "https://test.api.amadeus.com")

    # MakCorps (Hotels)
    MAKCORPS_API_KEY: str = os.getenv("MAKCORPS_API_KEY", "")
    MAKCORPS_BASE_URL: str = os.getenv("MAKCORPS_BASE_URL", "https://api.makcorps.com/free")

    # Email / SMTP
    SMTP_HOST: str = os.getenv("SMTP_HOST", "")
    SMTP_PORT: int = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USERNAME: str = os.getenv("SMTP_USERNAME", "")
    SMTP_PASSWORD: str = os.getenv("SMTP_PASSWORD", "")
    SMTP_USE_TLS: bool = os.getenv("SMTP_USE_TLS", "true").lower() == "true"
    EMAIL_SENDER: str = os.getenv("EMAIL_SENDER", os.getenv("SMTP_USERNAME", "no-reply@ai-travel-planner"))

    # Google OAuth (optional)
    GOOGLE_CLIENT_ID: str = os.getenv("GOOGLE_CLIENT_ID", "")
    GOOGLE_CLIENT_SECRET: str = os.getenv("GOOGLE_CLIENT_SECRET", "")
    GOOGLE_REDIRECT_URI: str = os.getenv("GOOGLE_REDIRECT_URI", "")

    # JWT
    JWT_SECRET: str = os.getenv("JWT_SECRET", "super_secret_stable_key_change_in_prod")
    JWT_ALGORITHM: str = os.getenv("JWT_ALGORITHM", "HS256")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))


config = Config()

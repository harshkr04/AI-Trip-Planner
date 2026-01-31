from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from .config import config

SQLALCHEMY_DATABASE_URL = config.DATABASE_URL

# Handle case where DATABASE_URL might be missing or empty during initial setup
if not SQLALCHEMY_DATABASE_URL:
    # Fallback to a local sqlite file for safety if no URL provided, 
    # though the plan requires a real DB. 
    # This prevents crash on import if env var is missing.
    SQLALCHEMY_DATABASE_URL = "sqlite:///./sql_app.db"

engine = create_engine(SQLALCHEMY_DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

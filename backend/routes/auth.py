# backend/routes/auth.py
from fastapi import APIRouter, HTTPException, Depends, Request
from sqlalchemy.orm import Session
from pydantic import BaseModel, EmailStr, constr
from google.oauth2 import id_token
from google.auth.transport import requests
import requests as req
from ..database import get_db
from ..models import User
from ..config import config
import urllib.parse
from passlib.context import CryptContext
import uuid
from datetime import datetime, timedelta
from jose import jwt

router = APIRouter()

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password):
    return pwd_context.hash(password)

class GoogleLoginRequest(BaseModel):
    token: str

class RegisterRequest(BaseModel):
    email: EmailStr
    password: constr(min_length=6)
    name: str

class LoginRequest(BaseModel):
    email: EmailStr
    password: str

class UpdateProfileRequest(BaseModel):
    id: str
    name: str
    email: EmailStr
    picture: str | None = None

@router.put("/update-profile")
def update_profile(payload: UpdateProfileRequest, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.id == payload.id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    
    # Check if email is being changed and if it's already taken
    if payload.email != user.email:
        existing_email = db.query(User).filter(User.email == payload.email).first()
        if existing_email:
            raise HTTPException(status_code=400, detail="Email already in use")
            
    user.name = payload.name
    user.email = payload.email
    user.picture = payload.picture
    
    db.commit()
    db.refresh(user)
    
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "picture": user.picture
        },
        "token": "session_token_placeholder" 
    }


@router.get("/google/config")
def get_google_config():
    """
    Returns the Google Client ID and whether the server is configured for Google Auth.
    """
    is_configured = bool(config.GOOGLE_CLIENT_ID and config.GOOGLE_CLIENT_SECRET)
    return {
        "configured": is_configured,
        "client_id": config.GOOGLE_CLIENT_ID if is_configured else None
    }

def create_access_token(data: dict, expires_delta: timedelta | None = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, config.JWT_SECRET, algorithm=config.JWT_ALGORITHM)
    return encoded_jwt

@router.post("/register", status_code=201)
def register(payload: RegisterRequest, db: Session = Depends(get_db)):
    try:
        # Check if user exists
        existing_user = db.query(User).filter(User.email == payload.email).first()
        if existing_user:
            print(f"[AUTH] Registration failed: Email {payload.email} already exists")
            raise HTTPException(status_code=409, detail="Email already registered")

        # Create new user
        hashed_pw = get_password_hash(payload.password)
        new_user = User(
            email=payload.email,
            name=payload.name,
            hashed_password=hashed_pw,
            picture="" # Default empty picture
        )
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        print(f"[AUTH] Registration successful: {new_user.email} (ID: {new_user.id})")

        # Generate JWT
        access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
        access_token = create_access_token(
            data={"sub": new_user.email, "id": new_user.id},
            expires_delta=access_token_expires
        )

        return {
            "user": {
                "id": new_user.id,
                "email": new_user.email,
                "name": new_user.name,
                "picture": new_user.picture
            },
            "token": access_token
        }
    except HTTPException:
        # Re-raise HTTP exceptions (like 409)
        raise
    except Exception as e:
        print(f"[AUTH] Registration error for {payload.email}: {str(e)}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to create account. Please try again.")

@router.post("/login")
def login(payload: LoginRequest, db: Session = Depends(get_db)):
    print(f"[AUTH] Login attempt for: {payload.email}")
    
    user = db.query(User).filter(User.email == payload.email).first()
    if not user or not user.hashed_password:
        # If user exists but has no password (e.g. google auth only), or doesn't exist
        print(f"[AUTH] Login failed: User not found or no password set for {payload.email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")
    
    if not verify_password(payload.password, user.hashed_password):
        print(f"[AUTH] Login failed: Invalid password for {payload.email}")
        raise HTTPException(status_code=401, detail="Invalid email or password")

    print(f"[AUTH] Login successful: {user.email} (ID: {user.id})")
    
    # Generate JWT
    access_token_expires = timedelta(minutes=config.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = create_access_token(
        data={"sub": user.email, "id": user.id},
        expires_delta=access_token_expires
    )
    
    return {
        "user": {
            "id": user.id,
            "email": user.email,
            "name": user.name,
            "picture": user.picture
        },
        "token": access_token
    }

# Keeping Google endpoints for potential future re-enablement or legacy support
@router.get("/google/start")
def start_google_auth():
    """
    Returns the URL to start the Google OAuth flow.
    """
    if not config.GOOGLE_CLIENT_ID or not config.GOOGLE_REDIRECT_URI:
        raise HTTPException(status_code=500, detail="Google Auth not configured on server.")
    
    params = {
        "client_id": config.GOOGLE_CLIENT_ID,
        "redirect_uri": config.GOOGLE_REDIRECT_URI,
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "consent"
    }
    url = f"https://accounts.google.com/o/oauth2/v2/auth?{urllib.parse.urlencode(params)}"
    return {"url": url}

class CallbackRequest(BaseModel):
    code: str

@router.post("/google/callback")
def google_callback(payload: CallbackRequest, db: Session = Depends(get_db)):
    """
    Exchanges the auth code for tokens and logs the user in.
    """
    if not config.GOOGLE_CLIENT_ID or not config.GOOGLE_CLIENT_SECRET:
        raise HTTPException(status_code=500, detail="Google Auth not configured.")

    # Exchange code for token
    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "client_id": config.GOOGLE_CLIENT_ID,
        "client_secret": config.GOOGLE_CLIENT_SECRET,
        "code": payload.code,
        "grant_type": "authorization_code",
        "redirect_uri": config.GOOGLE_REDIRECT_URI,
    }
    
    try:
        resp = req.post(token_url, data=data)
        if not resp.ok:
            raise ValueError(f"Failed to exchange code: {resp.text}")
        
        tokens = resp.json()
        id_token_str = tokens.get("id_token")
        
        # Verify ID token
        id_info = id_token.verify_oauth2_token(id_token_str, requests.Request(), config.GOOGLE_CLIENT_ID)
        
        email = id_info.get("email")
        name = id_info.get("name")
        picture = id_info.get("picture")
        
        if not email:
            raise ValueError("Email not found in token")

        # Upsert user
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(email=email, name=name, picture=picture)
            db.add(user)
        else:
            user.name = name
            user.picture = picture
        
        db.commit()
        db.refresh(user)
        
        return {
            "user": {
                "id": user.id,
                "email": user.email,
                "name": user.name,
                "picture": user.picture
            },
            "token": id_token_str 
        }

    except Exception as e:
        print(f"Auth error: {e}")
        raise HTTPException(status_code=400, detail=str(e))

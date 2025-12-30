from pydantic_settings import BaseSettings
from functools import lru_cache
from typing import Optional
import secrets

class Settings(BaseSettings):
    # App
    APP_NAME: str = "S1C0N API"
    DEBUG: bool = True
    
    # Database
    DATABASE_URL: str = "sqlite:///./s1c0n.db"
    
    # JWT
    SECRET_KEY: str = secrets.token_urlsafe(32)
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 24 hours
    
    # CORS
    FRONTEND_URL: str = "http://localhost:5173"
    
    # AI
    GEMINI_API_KEY: Optional[str] = None
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()

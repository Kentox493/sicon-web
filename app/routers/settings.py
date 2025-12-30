"""
Settings Router
API endpoints for user settings including API key management.
"""
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from pydantic import BaseModel
from typing import Optional

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.settings import UserSettings

router = APIRouter(prefix="/api/settings", tags=["Settings"])


class SettingsUpdate(BaseModel):
    gemini_api_key: Optional[str] = None


class SettingsResponse(BaseModel):
    has_gemini_key: bool
    gemini_key_preview: Optional[str] = None  # Show only last 4 chars


@router.get("/", response_model=SettingsResponse)
async def get_settings(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get current user settings."""
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    
    if not settings:
        return SettingsResponse(has_gemini_key=False)
    
    api_key = settings.get_api_key()
    return SettingsResponse(
        has_gemini_key=bool(api_key),
        gemini_key_preview=f"...{api_key[-4:]}" if api_key else None
    )


@router.put("/")
async def update_settings(
    data: SettingsUpdate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Update user settings."""
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    
    if not settings:
        settings = UserSettings(user_id=current_user.id)
        db.add(settings)
    
    if data.gemini_api_key is not None:
        settings.set_api_key(data.gemini_api_key)
    
    db.commit()
    db.refresh(settings)
    
    api_key = settings.get_api_key()
    return {
        "message": "Settings updated successfully",
        "has_gemini_key": bool(api_key),
        "gemini_key_preview": f"...{api_key[-4:]}" if api_key else None
    }


@router.delete("/gemini-key")
async def delete_gemini_key(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Remove Gemini API key."""
    settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
    
    if settings:
        settings.gemini_api_key = None
        db.commit()
    
    return {"message": "Gemini API key removed"}

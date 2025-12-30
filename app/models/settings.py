"""
User Settings Model
Stores user-specific settings including API keys (encrypted).
"""
from sqlalchemy import Column, Integer, String, ForeignKey, Text
from sqlalchemy.orm import relationship
from app.core.database import Base
import base64

class UserSettings(Base):
    __tablename__ = "user_settings"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True)
    
    # AI Settings (stored base64 encoded for basic obfuscation)
    gemini_api_key = Column(Text, nullable=True)
    
    # Other settings
    default_scan_options = Column(Text, nullable=True)  # JSON string
    
    user = relationship("User", back_populates="settings")
    
    def set_api_key(self, key: str):
        """Encode and store API key."""
        if key:
            self.gemini_api_key = base64.b64encode(key.encode()).decode()
        else:
            self.gemini_api_key = None
    
    def get_api_key(self) -> str:
        """Decode and return API key."""
        if self.gemini_api_key:
            return base64.b64decode(self.gemini_api_key.encode()).decode()
        return None

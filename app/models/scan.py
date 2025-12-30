from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, ForeignKey, JSON
from sqlalchemy.orm import relationship
from datetime import datetime
from app.core.database import Base

class Scan(Base):
    __tablename__ = "scans"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    target = Column(String(255), nullable=False)
    scan_type = Column(String(50), default="full")  # full, waf, port, subdo, etc.
    status = Column(String(20), default="pending")  # pending, running, completed, failed
    options = Column(JSON, default={})  # Store scan options as JSON
    
    # Results stored as JSON
    results = Column(JSON, default={})
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    started_at = Column(DateTime, nullable=True)
    completed_at = Column(DateTime, nullable=True)
    
    # Progress tracking
    progress = Column(Integer, default=0)
    current_module = Column(String(50), nullable=True)
    
    # Relationships
    user = relationship("User", back_populates="scans")


class Report(Base):
    __tablename__ = "reports"

    id = Column(Integer, primary_key=True, index=True)
    scan_id = Column(Integer, ForeignKey("scans.id"), nullable=False)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer, default=0)
    format = Column(String(20), default="json")  # json, pdf, html
    created_at = Column(DateTime, default=datetime.utcnow)

from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

# --- Scan Schemas ---

class ScanOptions(BaseModel):
    waf: bool = True
    port: bool = True
    subdo: bool = True
    cms: bool = True
    tech: bool = True
    dir: bool = True
    wp: bool = False
    proxy: Optional[str] = None
    user_agent: Optional[str] = None
    use_tor: bool = False

class ScanCreate(BaseModel):
    target: str
    options: ScanOptions = ScanOptions()

class ScanResponse(BaseModel):
    id: int
    target: str
    scan_type: str
    status: str
    progress: int
    current_module: Optional[str]
    results: Dict[str, Any]
    created_at: datetime
    started_at: Optional[datetime]
    completed_at: Optional[datetime]

    class Config:
        from_attributes = True

class ScanListResponse(BaseModel):
    id: int
    target: str
    scan_type: str
    status: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# --- Report Schemas ---

class ReportResponse(BaseModel):
    id: int
    scan_id: int
    filename: str
    file_size: int
    format: str
    created_at: datetime

    class Config:
        from_attributes = True

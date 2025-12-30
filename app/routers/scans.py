from fastapi import APIRouter, Depends, HTTPException, status, BackgroundTasks
from sqlalchemy.orm import Session
from typing import List

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.scan import Scan
from app.schemas.scan import ScanCreate, ScanResponse, ScanListResponse
from app.services.scanner import run_scan_task

router = APIRouter(prefix="/api/scans", tags=["Scans"])

@router.post("/", response_model=ScanResponse, status_code=status.HTTP_201_CREATED)
async def create_scan(
    scan_data: ScanCreate,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    db_scan = Scan(
        user_id=current_user.id,
        target=scan_data.target,
        scan_type="full" if all([scan_data.options.waf, scan_data.options.port, scan_data.options.subdo]) else "partial",
        status="pending",
        options=scan_data.options.model_dump()
    )
    db.add(db_scan)
    db.commit()
    db.refresh(db_scan)
    
    background_tasks.add_task(run_scan_task, db_scan.id, scan_data.options.model_dump())
    return db_scan

@router.get("/", response_model=List[ScanListResponse])
async def list_scans(skip: int = 0, limit: int = 20, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    scans = db.query(Scan).filter(Scan.user_id == current_user.id).order_by(Scan.created_at.desc()).offset(skip).limit(limit).all()
    return scans

@router.get("/{scan_id}", response_model=ScanResponse)
async def get_scan(scan_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    scan = db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == current_user.id).first()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
    return scan

@router.delete("/{scan_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_scan(scan_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    scan = db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == current_user.id).first()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
    db.delete(scan)
    db.commit()
    return None

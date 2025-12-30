from fastapi import APIRouter, Depends, HTTPException, status, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime
import io

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.scan import Scan, Report
from app.models.settings import UserSettings
from app.services.report_generator import generate_scan_report

router = APIRouter(prefix="/api/reports", tags=["Reports"])


@router.get("/")
async def list_reports(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Get list of generated reports for current user."""
    reports = db.query(Report).filter(Report.user_id == current_user.id).order_by(Report.created_at.desc()).all()
    return [
        {
            "id": r.id,
            "scan_id": r.scan_id,
            "filename": r.filename,
            "format": r.format,
            "file_size": r.file_size,
            "created_at": r.created_at.isoformat() if r.created_at else None
        }
        for r in reports
    ]


@router.post("/generate/{scan_id}")
async def generate_report(
    scan_id: int,
    use_ai: bool = Query(default=False, description="Use AI for executive summary"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Generate a PDF report for a specific scan."""
    # Get scan
    scan = db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == current_user.id).first()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
    
    if scan.status != "completed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Scan is not completed yet")
    
    # Get user's API key if using AI
    api_key = None
    if use_ai:
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
        if user_settings:
            api_key = user_settings.get_api_key()
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Gemini API key not configured. Please add your API key in Settings."
            )
    
    # Generate PDF
    try:
        scan_data = {
            "id": scan.id,
            "target": scan.target,
            "scan_type": scan.scan_type,
            "status": scan.status,
            "started_at": scan.started_at,
            "completed_at": scan.completed_at,
            "results": scan.results or {}
        }
        
        user_data = {
            "username": current_user.username,
            "email": current_user.email
        }
        
        pdf_bytes = generate_scan_report(scan_data, user_data, use_ai=use_ai, api_key=api_key)
        
        # Save report to database
        report_type = "ai" if use_ai else "standard"
        filename = f"S1C0N_{report_type.upper()}_{scan.target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        report = Report(
            scan_id=scan.id,
            user_id=current_user.id,
            filename=filename,
            file_path=f"/reports/{filename}",
            file_size=len(pdf_bytes),
            format="pdf"
        )
        db.add(report)
        db.commit()
        db.refresh(report)
        
        return {
            "id": report.id,
            "scan_id": scan.id,
            "filename": filename,
            "file_size": len(pdf_bytes),
            "used_ai": use_ai,
            "message": "Report generated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate report: {str(e)}")


@router.get("/download/{scan_id}")
async def download_report(
    scan_id: int,
    use_ai: bool = Query(default=False, description="Use AI for executive summary"),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Download PDF report for a specific scan."""
    # Get scan
    scan = db.query(Scan).filter(Scan.id == scan_id, Scan.user_id == current_user.id).first()
    if not scan:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Scan not found")
    
    if scan.status != "completed":
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Scan is not completed yet")
    
    # Get user's API key if using AI
    api_key = None
    if use_ai:
        user_settings = db.query(UserSettings).filter(UserSettings.user_id == current_user.id).first()
        if user_settings:
            api_key = user_settings.get_api_key()
        
        if not api_key:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST, 
                detail="Gemini API key not configured. Please add your API key in Settings."
            )
    
    # Generate PDF on-the-fly
    try:
        scan_data = {
            "id": scan.id,
            "target": scan.target,
            "scan_type": scan.scan_type,
            "status": scan.status,
            "started_at": scan.started_at,
            "completed_at": scan.completed_at,
            "results": scan.results or {}
        }
        
        user_data = {
            "username": current_user.username,
            "email": current_user.email
        }
        
        pdf_bytes = generate_scan_report(scan_data, user_data, use_ai=use_ai, api_key=api_key)
        
        report_type = "AI" if use_ai else "STANDARD"
        filename = f"S1C0N_{report_type}_{scan.target}_{scan.id}.pdf"
        
        return StreamingResponse(
            io.BytesIO(pdf_bytes),
            media_type="application/pdf",
            headers={
                "Content-Disposition": f"attachment; filename={filename}"
            }
        )
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate report: {str(e)}")


@router.delete("/{report_id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_report(
    report_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """Delete a report."""
    report = db.query(Report).filter(Report.id == report_id, Report.user_id == current_user.id).first()
    if not report:
        raise HTTPException(status_code=status.HTTP_404_NOT_FOUND, detail="Report not found")
    
    db.delete(report)
    db.commit()
    return None

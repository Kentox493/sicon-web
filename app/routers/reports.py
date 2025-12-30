from fastapi import APIRouter, Depends, HTTPException, status
from fastapi.responses import StreamingResponse
from sqlalchemy.orm import Session
from typing import List
from datetime import datetime
import io

from app.core.database import get_db
from app.core.security import get_current_user
from app.models.user import User
from app.models.scan import Scan, Report
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
        
        pdf_bytes = generate_scan_report(scan_data, user_data)
        
        # Save report to database
        filename = f"S1C0N_Report_{scan.target}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.pdf"
        
        report = Report(
            scan_id=scan.id,
            user_id=current_user.id,
            filename=filename,
            file_path=f"/reports/{filename}",  # Virtual path
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
            "message": "Report generated successfully"
        }
        
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"Failed to generate report: {str(e)}")


@router.get("/download/{scan_id}")
async def download_report(
    scan_id: int,
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
        
        pdf_bytes = generate_scan_report(scan_data, user_data)
        
        filename = f"S1C0N_Report_{scan.target}_{scan.id}.pdf"
        
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

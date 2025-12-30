from datetime import datetime
from typing import Dict, Any
from app.core.database import SessionLocal
from app.models.scan import Scan

def run_scan_task(scan_id: int, options: Dict[str, Any]):
    """Background task to run the scan."""
    db = SessionLocal()
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            return
        
        scan.status = "running"
        scan.started_at = datetime.utcnow()
        scan.progress = 0
        db.commit()
        
        target = scan.target
        results = {}
        modules_to_run = []
        
        if options.get("waf", True):
            modules_to_run.append("waf")
        if options.get("port", True):
            modules_to_run.append("port")
        if options.get("subdo", True):
            modules_to_run.append("subdo")
        if options.get("cms", True):
            modules_to_run.append("cms")
        if options.get("tech", True):
            modules_to_run.append("tech")
        if options.get("dir", True):
            modules_to_run.append("dir")
        if options.get("wp", False):
            modules_to_run.append("wp")
        
        total_modules = len(modules_to_run)
        
        for i, module in enumerate(modules_to_run):
            scan.current_module = module
            scan.progress = int((i / total_modules) * 100)
            db.commit()
            
            try:
                result = run_module(module, target, options)
                results[module] = result
            except Exception as e:
                results[module] = {"error": str(e)}
        
        scan.status = "completed"
        scan.progress = 100
        scan.current_module = None
        scan.completed_at = datetime.utcnow()
        scan.results = results
        db.commit()
        
    except Exception as e:
        if scan:
            scan.status = "failed"
            scan.results = {"error": str(e)}
            db.commit()
    finally:
        db.close()

def run_module(module: str, target: str, options: Dict[str, Any]) -> Dict[str, Any]:
    """Run a specific scan module and return results."""
    mock_results = {
        "waf": {"detected": True, "waf_name": "Cloudflare", "target": target},
        "port": {
            "open_ports": [
                {"port": 22, "service": "ssh", "version": "OpenSSH 8.2"},
                {"port": 80, "service": "http", "version": "nginx 1.18.0"},
                {"port": 443, "service": "https", "version": "nginx 1.18.0"},
            ]
        },
        "subdo": {
            "count": 5,
            "subdomains": [f"www.{target}", f"api.{target}", f"admin.{target}", f"mail.{target}", f"dev.{target}"]
        },
        "cms": {"detected": True, "cms_name": "WordPress", "version": "6.4.2"},
        "tech": {"technologies": ["nginx", "PHP", "MySQL", "jQuery", "Bootstrap"]},
        "dir": {
            "directories": [
                {"path": "/admin", "status": 403},
                {"path": "/wp-admin", "status": 200},
                {"path": "/login", "status": 200},
                {"path": "/.git", "status": 403},
            ]
        },
        "wp": {
            "plugins": [
                {"name": "contact-form-7", "version": "5.8.1", "vulnerable": False},
                {"name": "elementor", "version": "3.18.0", "vulnerable": True},
            ]
        }
    }
    
    return mock_results.get(module, {"status": "completed"})

"""
Scanner Service Module - Real Tool Execution

This module executes real security scanning tools with proper security validation.
Includes LFI protection and input sanitization.
"""

import subprocess
import re
import json
import os
import tempfile
import shutil
from datetime import datetime
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse
from app.core.database import SessionLocal
from app.models.scan import Scan

# =============================================================================
# SECURITY: Input Validation & Sanitization
# =============================================================================

def validate_target(target: str) -> str:
    """
    Validate and sanitize target input to prevent LFI and command injection.
    Returns cleaned domain/IP or raises ValueError.
    """
    if not target:
        raise ValueError("Target cannot be empty")
    
    # Remove any protocol prefix for domain extraction
    target = target.strip()
    
    # Parse URL to extract domain
    if target.startswith(('http://', 'https://')):
        parsed = urlparse(target)
        domain = parsed.netloc
    else:
        domain = target
    
    # Remove port if present
    if ':' in domain:
        domain = domain.split(':')[0]
    
    # Security: Block dangerous patterns (LFI, Command Injection)
    dangerous_patterns = [
        r'\.\./',           # Directory traversal
        r'\.\.',            # Parent directory
        r';',               # Command separator
        r'\|',              # Pipe
        r'&',               # Command chaining
        r'\$',              # Variable expansion
        r'`',               # Command substitution
        r'\n',              # Newline
        r'\r',              # Carriage return
        r'<',               # Redirect
        r'>',               # Redirect
        r'\x00',            # Null byte
        r'/etc/',           # Linux system paths
        r'/var/',
        r'/tmp/',
        r'/proc/',
        r'c:\\',            # Windows paths (case insensitive)
        r'file://',         # File protocol
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, domain, re.IGNORECASE):
            raise ValueError(f"Invalid target: contains dangerous pattern")
    
    # Validate domain format (alphanumeric, dots, hyphens only)
    domain_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9\-\.]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$'
    if not re.match(domain_pattern, domain):
        # Check if it's an IP address
        ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
        if not re.match(ip_pattern, domain):
            raise ValueError(f"Invalid target format: {domain}")
    
    return domain

def sanitize_command_arg(arg: str) -> str:
    """Sanitize a single command argument."""
    # Remove dangerous characters
    return re.sub(r'[;&|`$<>\n\r\x00]', '', arg)

# =============================================================================
# SCANNING FUNCTIONS
# =============================================================================

def run_scan_task(scan_id: int, options: Dict[str, Any]):
    """
    Background task to run the scan with real tools.
    """
    db = SessionLocal()
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            return
        
        # Validate target
        try:
            target = validate_target(scan.target)
        except ValueError as e:
            scan.status = "failed"
            scan.results = {"error": str(e)}
            db.commit()
            return
        
        scan.status = "running"
        scan.started_at = datetime.utcnow()
        scan.progress = 0
        db.commit()
        
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
        
        total_modules = len(modules_to_run) if modules_to_run else 1
        
        for i, module in enumerate(modules_to_run):
            scan.current_module = module
            scan.progress = int((i / total_modules) * 100)
            db.commit()
            
            try:
                result = run_module(module, target, options)
                results[module] = result
            except Exception as e:
                results[module] = {"error": str(e), "status": "failed"}
        
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
    proxy = options.get("proxy")
    user_agent = options.get("user_agent")
    
    module_handlers = {
        "waf": run_waf_scan,
        "port": run_port_scan,
        "subdo": run_subdomain_scan,
        "cms": run_cms_detection,
        "tech": run_tech_detection,
        "dir": run_directory_scan,
        "wp": run_wp_enum,
    }
    
    handler = module_handlers.get(module)
    if handler:
        return handler(target, proxy, user_agent)
    
    return {"status": "unknown_module"}

# =============================================================================
# WAF DETECTION
# =============================================================================

def run_waf_scan(target: str, proxy: Optional[str] = None, user_agent: Optional[str] = None) -> Dict[str, Any]:
    """Run WAF detection using wafw00f."""
    try:
        # First get the proper URL using httprobe equivalent
        try:
            probe_result = subprocess.run(
                ["httprobe"],
                input=target,
                capture_output=True,
                text=True,
                timeout=30
            )
            host = probe_result.stdout.strip() or f"https://{target}"
        except:
            host = f"https://{target}"
        
        # Run wafw00f
        cmd = ["wafw00f", host]
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = result.stdout
        
        if "is behind" in output:
            match = re.search(r'is behind\s(.+?)\s\(', output)
            if match:
                waf_name = match.group(1).strip()
                return {
                    "detected": True,
                    "waf_name": waf_name,
                    "target": host,
                    "raw_output": output[:500]
                }
        
        return {
            "detected": False,
            "waf_name": None,
            "target": host,
            "raw_output": output[:500]
        }
        
    except subprocess.TimeoutExpired:
        return {"error": "Timeout", "detected": False}
    except FileNotFoundError:
        return {"error": "wafw00f not installed", "detected": False}
    except Exception as e:
        return {"error": str(e), "detected": False}

# =============================================================================
# PORT SCANNING
# =============================================================================

def run_port_scan(target: str, proxy: Optional[str] = None, user_agent: Optional[str] = None) -> Dict[str, Any]:
    """Run port scan using nmap."""
    try:
        # Run nmap with service version detection
        cmd = ["nmap", "-sV", "-F", target]  # -F for fast scan (top 100 ports)
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        output = result.stdout
        
        # Parse nmap output
        open_ports = []
        for line in output.split('\n'):
            if '/tcp' in line and 'open' in line:
                parts = line.split()
                if len(parts) >= 3:
                    port_proto = parts[0]  # e.g., "80/tcp"
                    port = int(port_proto.split('/')[0])
                    state = parts[1]
                    service = parts[2] if len(parts) > 2 else "unknown"
                    version = ' '.join(parts[3:]) if len(parts) > 3 else ""
                    
                    open_ports.append({
                        "port": port,
                        "state": state,
                        "service": service,
                        "version": version
                    })
        
        return {
            "open_ports": open_ports,
            "count": len(open_ports),
            "raw_output": output[:1000]
        }
        
    except subprocess.TimeoutExpired:
        return {"error": "Timeout", "open_ports": []}
    except FileNotFoundError:
        return {"error": "nmap not installed", "open_ports": []}
    except Exception as e:
        return {"error": str(e), "open_ports": []}

# =============================================================================
# SUBDOMAIN ENUMERATION
# =============================================================================

def run_subdomain_scan(target: str, proxy: Optional[str] = None, user_agent: Optional[str] = None) -> Dict[str, Any]:
    """Run subdomain enumeration using subfinder, sublist3r, assetfinder."""
    subdomains = set()
    
    try:
        # Run subfinder
        try:
            result = subprocess.run(
                ["subfinder", "-d", target, "-silent"],
                capture_output=True,
                text=True,
                timeout=120
            )
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    subdomains.add(line.strip())
        except:
            pass
        
        # Run sublist3r
        try:
            result = subprocess.run(
                ["sublist3r", "-d", target, "-o", "/dev/stdout"],
                capture_output=True,
                text=True,
                timeout=120
            )
            for line in result.stdout.strip().split('\n'):
                if line.strip() and not line.startswith('['):
                    subdomains.add(line.strip())
        except:
            pass
        
        # Run assetfinder
        try:
            result = subprocess.run(
                ["assetfinder", "--subs-only", target],
                capture_output=True,
                text=True,
                timeout=60
            )
            for line in result.stdout.strip().split('\n'):
                if line.strip():
                    subdomains.add(line.strip())
        except:
            pass
        
        # Separate cPanel subdomains from regular ones
        cpanel_prefixes = ("cpanel.", "webdisk.", "webmail.", "cpcontacts.", "whm.", "autoconfig.", "mail.", "cpcalendars.", "autodiscover.")
        cpanel_subdomains = [s for s in subdomains if s.startswith(cpanel_prefixes)]
        regular_subdomains = [s for s in subdomains if not s.startswith(cpanel_prefixes)]
        
        return {
            "count": len(subdomains),
            "subdomains": list(regular_subdomains)[:100],  # Limit to 100
            "cpanel_subdomains": cpanel_subdomains[:50],
            "total_found": len(subdomains)
        }
        
    except Exception as e:
        return {"error": str(e), "subdomains": [], "count": 0}

# =============================================================================
# CMS DETECTION
# =============================================================================

def run_cms_detection(target: str, proxy: Optional[str] = None, user_agent: Optional[str] = None) -> Dict[str, Any]:
    """Detect CMS using pattern matching on HTTP response."""
    import requests
    
    try:
        headers = {"User-Agent": user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        proxies = {"http": proxy, "https": proxy} if proxy else None
        
        url = f"https://{target}"
        try:
            response = requests.get(url, headers=headers, timeout=30, proxies=proxies, verify=False)
        except:
            url = f"http://{target}"
            response = requests.get(url, headers=headers, timeout=30, proxies=proxies, verify=False)
        
        text = response.text
        
        # CMS detection patterns
        cms_patterns = {
            "WordPress": [r'wp-content', r'wp-includes', r'<meta name="generator" content="WordPress'],
            "Joomla": [r'/media/system/js/', r'<meta name="generator" content="Joomla'],
            "Drupal": [r'/sites/all/', r'<meta name="generator" content="Drupal'],
            "Moodle": [r'<meta name="keywords" content="moodle'],
            "Shopify": [r'cdn.shopify.com', r'Shopify.theme'],
            "Magento": [r'/skin/frontend/', r'Mage.Cookies'],
            "Laravel": [],  # Check via cookies
        }
        
        detected_cms = None
        version = None
        
        for cms, patterns in cms_patterns.items():
            for pattern in patterns:
                if re.search(pattern, text, re.IGNORECASE):
                    detected_cms = cms
                    break
            if detected_cms:
                break
        
        # Check Laravel via cookies
        if not detected_cms:
            if 'laravel_session' in response.cookies or 'XSRF-TOKEN' in response.cookies:
                detected_cms = "Laravel"
        
        # Try to extract version for WordPress
        if detected_cms == "WordPress":
            match = re.search(r'<meta name="generator" content="WordPress ([\d.]+)"', text)
            if match:
                version = match.group(1)
        
        return {
            "detected": detected_cms is not None,
            "cms_name": detected_cms,
            "version": version,
            "url": url
        }
        
    except Exception as e:
        return {"error": str(e), "detected": False, "cms_name": None}

# =============================================================================
# TECHNOLOGY DETECTION
# =============================================================================

def run_tech_detection(target: str, proxy: Optional[str] = None, user_agent: Optional[str] = None) -> Dict[str, Any]:
    """Detect web technologies using headers and response analysis."""
    import requests
    
    try:
        headers = {"User-Agent": user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        proxies = {"http": proxy, "https": proxy} if proxy else None
        
        url = f"https://{target}"
        try:
            response = requests.get(url, headers=headers, timeout=30, proxies=proxies, verify=False)
        except:
            url = f"http://{target}"
            response = requests.get(url, headers=headers, timeout=30, proxies=proxies, verify=False)
        
        technologies = []
        
        # Check headers
        server = response.headers.get('Server', '')
        if 'nginx' in server.lower():
            technologies.append(f"nginx ({server.split('/')[1] if '/' in server else ''})")
        elif 'apache' in server.lower():
            technologies.append(f"Apache ({server})")
        elif 'cloudflare' in server.lower():
            technologies.append("Cloudflare")
        
        powered_by = response.headers.get('X-Powered-By', '')
        if powered_by:
            technologies.append(powered_by)
        
        # Check response body
        text = response.text
        
        tech_patterns = {
            "jQuery": r'jquery[.-]?\d*\.?\d*\.?min\.js|jquery\.js',
            "Bootstrap": r'bootstrap[.-]?\d*\.?\d*\.?(min\.)?css',
            "React": r'react[.-]?\d*\.?\d*\.?min\.js|__REACT',
            "Vue.js": r'vue[.-]?\d*\.?\d*\.?min\.js|v-if|v-for',
            "Angular": r'angular[.-]?\d*\.?\d*\.?min\.js|ng-app',
            "Tailwind CSS": r'tailwindcss|tailwind\.css',
            "Font Awesome": r'font-awesome|fontawesome',
            "Google Analytics": r'google-analytics\.com|gtag\.js',
            "Google Tag Manager": r'googletagmanager\.com',
        }
        
        for tech, pattern in tech_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                technologies.append(tech)
        
        return {
            "technologies": list(set(technologies)),
            "count": len(technologies),
            "url": url
        }
        
    except Exception as e:
        return {"error": str(e), "technologies": []}

# =============================================================================
# DIRECTORY SCANNING
# =============================================================================

def run_directory_scan(target: str, proxy: Optional[str] = None, user_agent: Optional[str] = None) -> Dict[str, Any]:
    """Run directory scanning using dirsearch."""
    try:
        # Create temporary file for output
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name
        
        cmd = ["dirsearch", "-u", f"https://{target}", "-o", output_file, "--format=json", "-q"]
        
        if user_agent:
            cmd.extend(["--user-agent", sanitize_command_arg(user_agent)])
        if proxy:
            cmd.extend(["--proxy", sanitize_command_arg(proxy)])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        directories = []
        
        if os.path.exists(output_file):
            try:
                with open(output_file, 'r') as f:
                    data = json.load(f)
                    if "results" in data:
                        for item in data["results"][:100]:  # Limit to 100
                            directories.append({
                                "path": item.get("url", ""),
                                "status": item.get("status", 0),
                                "size": item.get("content-length", 0)
                            })
            except:
                pass
            finally:
                os.unlink(output_file)
        
        return {
            "directories": directories,
            "count": len(directories)
        }
        
    except subprocess.TimeoutExpired:
        return {"error": "Timeout", "directories": []}
    except FileNotFoundError:
        return {"error": "dirsearch not installed", "directories": []}
    except Exception as e:
        return {"error": str(e), "directories": []}

# =============================================================================
# WORDPRESS ENUMERATION
# =============================================================================

def run_wp_enum(target: str, proxy: Optional[str] = None, user_agent: Optional[str] = None) -> Dict[str, Any]:
    """Run WordPress enumeration using wpscan."""
    try:
        cmd = ["wpscan", "--url", f"https://{target}", "--enumerate", "p,t,u", "--format", "json"]
        
        if proxy:
            cmd.extend(["--proxy", sanitize_command_arg(proxy)])
        
        result = subprocess.run(cmd, capture_output=True, text=True, timeout=600)
        
        try:
            data = json.loads(result.stdout)
            
            plugins = []
            themes = []
            users = []
            
            if "plugins" in data:
                for name, info in data["plugins"].items():
                    plugins.append({
                        "name": name,
                        "version": info.get("version", {}).get("number", "unknown"),
                        "vulnerable": len(info.get("vulnerabilities", [])) > 0
                    })
            
            if "themes" in data:
                for name, info in data["themes"].items():
                    themes.append({
                        "name": name,
                        "version": info.get("version", {}).get("number", "unknown")
                    })
            
            if "users" in data:
                for user in data["users"]:
                    users.append(user.get("username", ""))
            
            return {
                "plugins": plugins[:50],
                "themes": themes[:20],
                "users": users[:20],
                "wp_version": data.get("version", {}).get("number", "unknown")
            }
            
        except json.JSONDecodeError:
            return {"error": "Failed to parse wpscan output", "plugins": [], "themes": [], "users": []}
        
    except subprocess.TimeoutExpired:
        return {"error": "Timeout", "plugins": [], "themes": [], "users": []}
    except FileNotFoundError:
        return {"error": "wpscan not installed", "plugins": [], "themes": [], "users": []}
    except Exception as e:
        return {"error": str(e), "plugins": [], "themes": [], "users": []}

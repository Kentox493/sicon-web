"""
Scanner Service Module - Real Tool Execution with Clean Output Parsing

This module executes real security scanning tools and returns clean, structured JSON output.
Includes LFI protection and input sanitization.
"""

import subprocess
import re
import json
import os
import tempfile
import time
import requests
from datetime import datetime
from typing import Dict, Any, Optional, List
from urllib.parse import urlparse
from app.core.database import SessionLocal
from app.models.scan import Scan

# Disable SSL warnings for scanning
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

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
    
    # Security: Block dangerous patterns
    dangerous_patterns = [
        r'\.\.\/', r'\.\.', r';', r'\|', r'&', r'\$', r'`', r'\n', r'\r',
        r'<', r'>', r'\x00', r'/etc/', r'/var/', r'/tmp/', r'/proc/',
        r'c:\\', r'file://',
    ]
    
    for pattern in dangerous_patterns:
        if re.search(pattern, domain, re.IGNORECASE):
            raise ValueError(f"Invalid target: contains dangerous pattern")
    
    # Validate domain format
    domain_pattern = r'^[a-zA-Z0-9][a-zA-Z0-9\-\.]*[a-zA-Z0-9]$|^[a-zA-Z0-9]$'
    ip_pattern = r'^(\d{1,3}\.){3}\d{1,3}$'
    
    if not re.match(domain_pattern, domain) and not re.match(ip_pattern, domain):
        raise ValueError(f"Invalid target format: {domain}")
    
    return domain

def sanitize_command_arg(arg: str) -> str:
    """Sanitize command argument."""
    return re.sub(r'[;&|`$<>\n\r\x00]', '', arg)

# =============================================================================
# MAIN SCAN TASK
# =============================================================================

def run_scan_task(scan_id: int, options: Dict[str, Any]):
    """Background task to run the scan with real tools."""
    db = SessionLocal()
    try:
        scan = db.query(Scan).filter(Scan.id == scan_id).first()
        if not scan:
            return
        
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
    """Run a specific scan module."""
    proxy = options.get("proxy")
    user_agent = options.get("user_agent")
    
    handlers = {
        "waf": run_waf_scan,
        "port": run_port_scan,
        "subdo": run_subdomain_scan,
        "cms": run_cms_detection,
        "tech": run_tech_detection,
        "dir": run_directory_scan,
        "wp": run_wp_enum,
    }
    
    handler = handlers.get(module)
    if handler:
        return handler(target, proxy, user_agent)
    
    return {"status": "unknown_module"}

# =============================================================================
# WAF DETECTION - Clean Output
# =============================================================================

def run_waf_scan(target: str, proxy: Optional[str] = None, user_agent: Optional[str] = None) -> Dict[str, Any]:
    """Run WAF detection using wafw00f with clean parsed output."""
    result = {
        "detected": False,
        "waf_name": None,
        "waf_vendor": None,
        "target": target,
        "status": "completed"
    }
    
    try:
        # Try HTTPS first
        host = f"https://{target}"
        
        cmd = ["wafw00f", host, "-o", "-"]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=60)
        output = proc.stdout + proc.stderr
        
        # Parse output
        if "is behind" in output:
            # Extract: "The site https://example.com is behind Cloudflare (Cloudflare Inc.)"
            match = re.search(r'is behind\s+(.+?)\s*(?:\(([^)]+)\))?(?:\s|$)', output)
            if match:
                result["detected"] = True
                result["waf_name"] = match.group(1).strip()
                result["waf_vendor"] = match.group(2).strip() if match.group(2) else None
        elif "No WAF" in output or "seems to be unprotected" in output:
            result["detected"] = False
            result["waf_name"] = "None"
        
        result["target"] = host
        
    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        result["error"] = "Scan timed out after 60 seconds"
    except FileNotFoundError:
        result["status"] = "error"
        result["error"] = "wafw00f not installed. Run: sudo apt install wafw00f"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    return result

# =============================================================================
# PORT SCANNING - Clean Output
# =============================================================================

def run_port_scan(target: str, proxy: Optional[str] = None, user_agent: Optional[str] = None) -> Dict[str, Any]:
    """Run port scan using nmap with clean parsed output."""
    result = {
        "open_ports": [],
        "count": 0,
        "target": target,
        "status": "completed",
        "scan_type": "Top 100 Ports (Fast Scan)"
    }
    
    try:
        cmd = ["nmap", "-sV", "-F", "--open", target]
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        output = proc.stdout
        
        # Parse nmap output line by line
        for line in output.split('\n'):
            # Match lines like: 22/tcp   open  ssh     OpenSSH 8.2p1 Ubuntu
            match = re.match(r'(\d+)/(\w+)\s+open\s+(\S+)\s*(.*)', line)
            if match:
                port_num = int(match.group(1))
                protocol = match.group(2)
                service = match.group(3)
                version = match.group(4).strip() if match.group(4) else ""
                
                # Determine risk level based on common vulnerable ports
                risk = "low"
                if port_num in [21, 23, 3389, 5900]:  # FTP, Telnet, RDP, VNC
                    risk = "high"
                elif port_num in [22, 25, 110, 143, 3306, 5432]:  # SSH, SMTP, POP3, IMAP, MySQL, PostgreSQL
                    risk = "medium"
                
                result["open_ports"].append({
                    "port": port_num,
                    "protocol": protocol,
                    "state": "open",
                    "service": service,
                    "version": version,
                    "risk": risk
                })
        
        result["count"] = len(result["open_ports"])
        
    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        result["error"] = "Scan timed out after 5 minutes"
    except FileNotFoundError:
        result["status"] = "error"
        result["error"] = "nmap not installed. Run: sudo apt install nmap"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    return result

# =============================================================================
# SUBDOMAIN ENUMERATION - Clean Output
# =============================================================================

def run_subdomain_scan(target: str, proxy: Optional[str] = None, user_agent: Optional[str] = None) -> Dict[str, Any]:
    """Run subdomain enumeration with clean parsed output."""
    result = {
        "subdomains": [],
        "count": 0,
        "sources": [],
        "target": target,
        "status": "completed"
    }
    
    all_subdomains = set()
    
    # Run subfinder
    try:
        proc = subprocess.run(
            ["subfinder", "-d", target, "-silent"],
            capture_output=True, text=True, timeout=120
        )
        for line in proc.stdout.strip().split('\n'):
            if line.strip() and '.' in line:
                all_subdomains.add(line.strip().lower())
        if proc.returncode == 0:
            result["sources"].append("subfinder")
    except:
        pass
    
    # Run assetfinder
    try:
        proc = subprocess.run(
            ["assetfinder", "--subs-only", target],
            capture_output=True, text=True, timeout=60
        )
        for line in proc.stdout.strip().split('\n'):
            if line.strip() and '.' in line:
                all_subdomains.add(line.strip().lower())
        if proc.returncode == 0:
            result["sources"].append("assetfinder")
    except:
        pass
    
    # Categorize subdomains
    cpanel_prefixes = ("cpanel.", "webdisk.", "webmail.", "cpcontacts.", "whm.", 
                       "autoconfig.", "mail.", "cpcalendars.", "autodiscover.")
    
    parsed_subdomains = []
    for sub in sorted(all_subdomains):
        sub_type = "cpanel" if sub.startswith(cpanel_prefixes) else "regular"
        parsed_subdomains.append({
            "subdomain": sub,
            "type": sub_type,
            "url": f"https://{sub}"
        })
    
    result["subdomains"] = parsed_subdomains[:100]  # Limit to 100
    result["count"] = len(all_subdomains)
    result["total_found"] = len(all_subdomains)
    
    if not result["sources"]:
        result["status"] = "error"
        result["error"] = "No subdomain tools available. Install: subfinder, assetfinder"
    
    return result

# =============================================================================
# CMS DETECTION - Clean Output
# =============================================================================

def run_cms_detection(target: str, proxy: Optional[str] = None, user_agent: Optional[str] = None) -> Dict[str, Any]:
    """Detect CMS with clean structured output."""
    result = {
        "detected": False,
        "cms_name": None,
        "cms_version": None,
        "confidence": "low",
        "indicators": [],
        "target": target,
        "status": "completed"
    }
    
    try:
        headers = {
            "User-Agent": user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        proxies = {"http": proxy, "https": proxy} if proxy else None
        
        # Try HTTPS first, fallback to HTTP
        url = f"https://{target}"
        try:
            resp = requests.get(url, headers=headers, timeout=15, proxies=proxies, verify=False, allow_redirects=True)
        except:
            url = f"http://{target}"
            resp = requests.get(url, headers=headers, timeout=15, proxies=proxies, verify=False, allow_redirects=True)
        
        text = resp.text
        
        # CMS Detection with confidence scoring
        cms_signatures = {
            "WordPress": {
                "patterns": [r'/wp-content/', r'/wp-includes/', r'wp-json'],
                "meta": r'<meta name="generator" content="WordPress ([\d.]+)"',
            },
            "Joomla": {
                "patterns": [r'/media/system/js/', r'/components/com_'],
                "meta": r'<meta name="generator" content="Joomla[!]?\s*([\d.]*)"',
            },
            "Drupal": {
                "patterns": [r'/sites/all/', r'/sites/default/', r'Drupal.settings'],
                "meta": r'<meta name="Generator" content="Drupal ([\d.]+)"',
            },
            "Shopify": {
                "patterns": [r'cdn\.shopify\.com', r'Shopify\.theme'],
                "meta": None,
            },
            "Laravel": {
                "patterns": [],
                "cookies": ['laravel_session', 'XSRF-TOKEN'],
            },
            "Magento": {
                "patterns": [r'/skin/frontend/', r'Mage\.Cookies', r'/static/frontend/'],
                "meta": None,
            },
        }
        
        for cms, sigs in cms_signatures.items():
            score = 0
            indicators = []
            version = None
            
            # Check patterns
            for pattern in sigs.get("patterns", []):
                if re.search(pattern, text, re.IGNORECASE):
                    score += 1
                    indicators.append(f"Found: {pattern}")
            
            # Check meta generator
            if sigs.get("meta"):
                match = re.search(sigs["meta"], text, re.IGNORECASE)
                if match:
                    score += 2
                    version = match.group(1) if match.groups() else None
                    indicators.append("Generator meta tag found")
            
            # Check cookies
            for cookie in sigs.get("cookies", []):
                if cookie in resp.cookies:
                    score += 2
                    indicators.append(f"Cookie: {cookie}")
            
            if score > 0:
                result["detected"] = True
                result["cms_name"] = cms
                result["cms_version"] = version
                result["indicators"] = indicators
                result["confidence"] = "high" if score >= 3 else "medium" if score >= 2 else "low"
                break
        
        result["url"] = url
        result["http_status"] = resp.status_code
        
    except requests.RequestException as e:
        result["status"] = "error"
        result["error"] = f"Connection failed: {str(e)}"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    return result

# =============================================================================
# TECHNOLOGY DETECTION - Clean Output
# =============================================================================

def run_tech_detection(target: str, proxy: Optional[str] = None, user_agent: Optional[str] = None) -> Dict[str, Any]:
    """Detect web technologies with categorized output."""
    result = {
        "technologies": [],
        "categories": {},
        "headers": {},
        "target": target,
        "status": "completed"
    }
    
    try:
        headers = {"User-Agent": user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"}
        proxies = {"http": proxy, "https": proxy} if proxy else None
        
        url = f"https://{target}"
        try:
            resp = requests.get(url, headers=headers, timeout=15, proxies=proxies, verify=False)
        except:
            url = f"http://{target}"
            resp = requests.get(url, headers=headers, timeout=15, proxies=proxies, verify=False)
        
        text = resp.text
        found_tech = []
        categories = {
            "web_server": [],
            "programming": [],
            "javascript": [],
            "css_framework": [],
            "analytics": [],
            "cdn": [],
            "other": []
        }
        
        # Server header
        server = resp.headers.get('Server', '')
        if server:
            result["headers"]["Server"] = server
            if 'nginx' in server.lower():
                found_tech.append({"name": "nginx", "version": server, "category": "web_server"})
                categories["web_server"].append("nginx")
            elif 'apache' in server.lower():
                found_tech.append({"name": "Apache", "version": server, "category": "web_server"})
                categories["web_server"].append("Apache")
            elif 'cloudflare' in server.lower():
                found_tech.append({"name": "Cloudflare", "category": "cdn"})
                categories["cdn"].append("Cloudflare")
        
        # X-Powered-By
        powered = resp.headers.get('X-Powered-By', '')
        if powered:
            result["headers"]["X-Powered-By"] = powered
            found_tech.append({"name": powered, "category": "programming"})
            categories["programming"].append(powered)
        
        # Content analysis
        tech_patterns = {
            ("jQuery", "javascript"): r'jquery[.\-]?\d*\.?\d*\.?(min\.)?js',
            ("Bootstrap", "css_framework"): r'bootstrap[.\-]?\d*\.?(min\.)?css',
            ("React", "javascript"): r'react[.\-]?dom|__REACT|_react',
            ("Vue.js", "javascript"): r'vue[.\-]?\d*\.?\d*\.?min\.js|v-if=|v-for=',
            ("Angular", "javascript"): r'angular[.\-]?\d*\.?min\.js|ng-app|ng-controller',
            ("Tailwind CSS", "css_framework"): r'tailwindcss|tailwind\.min\.css',
            ("Font Awesome", "css_framework"): r'font-?awesome|fa-[a-z]+-',
            ("Google Analytics", "analytics"): r'google-analytics\.com/analytics|gtag\s*\(',
            ("Google Tag Manager", "analytics"): r'googletagmanager\.com/gtm',
            ("Cloudflare", "cdn"): r'cdnjs\.cloudflare\.com|cloudflare\.com',
        }
        
        for (tech, cat), pattern in tech_patterns.items():
            if re.search(pattern, text, re.IGNORECASE):
                if not any(t["name"] == tech for t in found_tech):
                    found_tech.append({"name": tech, "category": cat})
                    categories[cat].append(tech)
        
        result["technologies"] = found_tech
        result["categories"] = {k: v for k, v in categories.items() if v}
        result["count"] = len(found_tech)
        result["url"] = url
        
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    return result

# =============================================================================
# DIRECTORY SCANNING - Clean Output
# =============================================================================

def run_directory_scan(target: str, proxy: Optional[str] = None, user_agent: Optional[str] = None) -> Dict[str, Any]:
    """Run directory scanning with clean parsed output."""
    result = {
        "directories": [],
        "count": 0,
        "by_status": {},
        "target": target,
        "status": "completed"
    }
    
    try:
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            output_file = f.name
        
        url = f"https://{target}"
        cmd = ["dirsearch", "-u", url, "-o", output_file, "--format=json", "-q", "-t", "20"]
        
        if user_agent:
            cmd.extend(["--user-agent", sanitize_command_arg(user_agent)])
        if proxy:
            cmd.extend(["--proxy", sanitize_command_arg(proxy)])
        
        proc = subprocess.run(cmd, capture_output=True, text=True, timeout=300)
        
        directories = []
        status_count = {"200": 0, "301": 0, "302": 0, "403": 0, "500": 0}
        
        if os.path.exists(output_file):
            try:
                with open(output_file, 'r') as f:
                    data = json.load(f)
                    for item in data.get("results", [])[:100]:
                        status = item.get("status", 0)
                        path = item.get("path", item.get("url", ""))
                        
                        # Determine severity
                        severity = "info"
                        if status == 200:
                            severity = "success"
                        elif status == 403:
                            severity = "warning"
                        elif status >= 500:
                            severity = "error"
                        
                        directories.append({
                            "path": path,
                            "status": status,
                            "size": item.get("content-length", 0),
                            "redirect": item.get("redirect", ""),
                            "severity": severity
                        })
                        
                        status_key = str(status)
                        status_count[status_key] = status_count.get(status_key, 0) + 1
            finally:
                os.unlink(output_file)
        
        # Sort by status code
        result["directories"] = sorted(directories, key=lambda x: x["status"])
        result["count"] = len(directories)
        result["by_status"] = {k: v for k, v in status_count.items() if v > 0}
        
    except subprocess.TimeoutExpired:
        result["status"] = "timeout"
        result["error"] = "Scan timed out after 5 minutes"
    except FileNotFoundError:
        result["status"] = "error"
        result["error"] = "dirsearch not installed. Run: pip install dirsearch"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    return result

# =============================================================================
# WORDPRESS ENUMERATION - Integrated with Core WP Modules
# =============================================================================

def run_wp_enum(target: str, proxy: Optional[str] = None, user_agent: Optional[str] = None) -> Dict[str, Any]:
    """
    Run WordPress enumeration using core logic from scan/wp modules.
    Discovers plugins, extracts versions, checks for outdated status, and finds vulnerabilities.
    """
    result = {
        "wordpress_detected": False,
        "version": None,
        "plugins": [],
        "themes": [],
        "users": [],
        "vulnerabilities": [],
        "target": target,
        "status": "completed"
    }
    
    try:
        headers = {
            "User-Agent": user_agent or "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36"
        }
        proxies = {"http": proxy, "https": proxy} if proxy else None
        
        # Try HTTPS first, fallback to HTTP
        url = f"https://{target}"
        try:
            resp = requests.get(url, headers=headers, timeout=15, proxies=proxies, verify=False, allow_redirects=True)
        except:
            url = f"http://{target}"
            resp = requests.get(url, headers=headers, timeout=15, proxies=proxies, verify=False, allow_redirects=True)
        
        page_content = resp.text
        
        # Check if WordPress
        wp_indicators = ['/wp-content/', '/wp-includes/', 'wp-json', 'WordPress']
        is_wp = any(ind in page_content for ind in wp_indicators)
        
        if not is_wp:
            result["wordpress_detected"] = False
            result["status"] = "completed"
            return result
        
        result["wordpress_detected"] = True
        
        # Extract WordPress version from meta generator
        version_match = re.search(r'<meta name="generator" content="WordPress ([\d.]+)"', page_content)
        if version_match:
            result["version"] = version_match.group(1)
        
        # Discover plugins from page content (core logic from wppluggin.py)
        plugins = set(re.findall(r"/wp-content/plugins/([a-zA-Z0-9\-_]+)/", page_content))
        
        # Discover themes from page content
        themes = set(re.findall(r"/wp-content/themes/([a-zA-Z0-9\-_]+)/", page_content))
        
        # Process each plugin (core logic from check_pluggin.py and cek_db.py)
        for plugin in list(plugins)[:20]:  # Limit to 20 plugins
            plugin_info = {
                "name": plugin,
                "version": None,
                "outdated": False,
                "vulnerabilities": 0,
                "vulnerable": False
            }
            
            # Try to get version from changelog.txt or readme.txt
            for file in ["readme.txt", "changelog.txt"]:
                try:
                    plugin_url = f"{url}/wp-content/plugins/{plugin}/{file}"
                    presp = requests.get(plugin_url, headers=headers, timeout=10, proxies=proxies, verify=False)
                    if presp.status_code == 200:
                        # Extract version from Stable tag or Changelog
                        stable_match = re.search(r'Stable tag:\s*([\d.]+)', presp.text, re.IGNORECASE)
                        changelog_match = re.search(r'= ([\d.]+) - \d{4}-\d{2}-\d{2} =', presp.text)
                        version_header = re.search(r'Version:\s*([\d.]+)', presp.text)
                        
                        if stable_match:
                            plugin_info["version"] = stable_match.group(1)
                        elif changelog_match:
                            plugin_info["version"] = changelog_match.group(1)
                        elif version_header:
                            plugin_info["version"] = version_header.group(1)
                        
                        if plugin_info["version"]:
                            break
                except:
                    continue
            
            # Check latest version from wordpress.org (core logic from cek_db.py)
            if plugin_info["version"]:
                try:
                    wp_org_url = f"https://wordpress.org/plugins/{plugin}/"
                    wp_resp = requests.get(wp_org_url, headers=headers, timeout=10, verify=False)
                    if wp_resp.status_code == 200:
                        latest_match = re.search(r'Version\s*<strong>([\d.]+)</strong>', wp_resp.text)
                        if latest_match:
                            latest_version = latest_match.group(1)
                            if plugin_info["version"] < latest_version:
                                plugin_info["outdated"] = True
                except:
                    pass
            
            # Check for vulnerabilities (simplified from cek_vuln.py)
            if plugin_info["version"]:
                try:
                    wpscan_url = f"https://wpscan.com/plugin/{plugin}"
                    vuln_resp = requests.get(wpscan_url, headers=headers, timeout=10, verify=False)
                    if vuln_resp.status_code == 200:
                        # Count vulnerabilities affecting this version
                        vuln_versions = re.findall(r'Fixed in\s+([\d.]+)', vuln_resp.text)
                        vuln_titles = re.findall(r'Title\s*</div>\s*<a href="[^"]+">([^<]+)', vuln_resp.text)
                        
                        vuln_count = 0
                        for vuln_ver, title in zip(vuln_versions, vuln_titles):
                            try:
                                if tuple(map(int, plugin_info["version"].split('.')[:3])) <= tuple(map(int, vuln_ver.split('.')[:3])):
                                    vuln_count += 1
                                    result["vulnerabilities"].append({
                                        "component": f"Plugin: {plugin}",
                                        "title": title.strip(),
                                        "type": "unknown",
                                        "severity": "high" if "critical" in title.lower() else "medium"
                                    })
                            except:
                                continue
                        
                        plugin_info["vulnerabilities"] = vuln_count
                        plugin_info["vulnerable"] = vuln_count > 0
                except:
                    pass
            
            result["plugins"].append(plugin_info)
        
        # Process themes
        for theme in list(themes)[:10]:  # Limit to 10 themes
            theme_info = {
                "name": theme,
                "version": None,
                "outdated": False
            }
            
            # Try to get theme version from style.css
            try:
                style_url = f"{url}/wp-content/themes/{theme}/style.css"
                sresp = requests.get(style_url, headers=headers, timeout=10, proxies=proxies, verify=False)
                if sresp.status_code == 200:
                    version_match = re.search(r'Version:\s*([\d.]+)', sresp.text)
                    if version_match:
                        theme_info["version"] = version_match.group(1)
            except:
                pass
            
            result["themes"].append(theme_info)
        
        # User enumeration via wp-json API
        try:
            users_url = f"{url}/wp-json/wp/v2/users"
            uresp = requests.get(users_url, headers=headers, timeout=10, proxies=proxies, verify=False)
            if uresp.status_code == 200:
                users_data = uresp.json()
                for user in users_data[:20]:
                    result["users"].append({
                        "id": user.get("id"),
                        "username": user.get("slug") or user.get("name", "")
                    })
        except:
            # Fallback: Try author archive enumeration
            for i in range(1, 11):
                try:
                    author_url = f"{url}/?author={i}"
                    aresp = requests.get(author_url, headers=headers, timeout=5, proxies=proxies, verify=False, allow_redirects=False)
                    if aresp.status_code == 301 or aresp.status_code == 302:
                        location = aresp.headers.get("Location", "")
                        author_match = re.search(r'/author/([^/]+)', location)
                        if author_match:
                            result["users"].append({
                                "id": i,
                                "username": author_match.group(1)
                            })
                except:
                    continue
        
    except requests.RequestException as e:
        result["status"] = "error"
        result["error"] = f"Connection failed: {str(e)}"
    except Exception as e:
        result["status"] = "error"
        result["error"] = str(e)
    
    return result


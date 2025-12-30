"""
AI Summary Service - Enhanced Analysis
Generates professional executive summaries with CVE lookup and findings table.
"""
from google import genai
from google.genai import types
import json

def generate_ai_summary(scan_data: dict, api_key: str = None) -> dict:
    """
    Generates an enhanced executive summary using Gemini API.
    Returns dict with 'summary' and 'findings' (list for table).
    Falls back to basic summary if API fails.
    """
    if not api_key:
        return {
            "summary": generate_basic_summary(scan_data),
            "findings": []
        }
        
    try:
        client = genai.Client(api_key=api_key)
        
        # Prepare comprehensive context
        target = scan_data.get('target', 'Unknown')
        results = scan_data.get('results', {})
        
        waf = results.get('waf', {})
        ports = results.get('port', {}).get('open_ports', [])
        subdomains = results.get('subdo', {}).get('subdomains', [])
        subdomain_count = results.get('subdo', {}).get('count', 0)
        cms = results.get('cms', {})
        tech = results.get('tech', {}).get('technologies', [])
        directories = results.get('dir', {}).get('directories', [])
        
        # Build detailed context for AI
        ports_detail = ""
        for p in ports[:15]:
            ports_detail += f"  - Port {p.get('port')}/{p.get('protocol', 'tcp')}: {p.get('service', 'unknown')} v{p.get('version', 'unknown')} (Risk: {p.get('risk', 'low')})\n"
        
        tech_detail = ""
        for t in tech[:10]:
            if isinstance(t, dict):
                tech_detail += f"  - {t.get('name', 'Unknown')} (Category: {t.get('category', 'General')})\n"
            else:
                tech_detail += f"  - {t}\n"
        
        dirs_detail = ""
        for d in directories[:10]:
            dirs_detail += f"  - {d.get('path')} (Status: {d.get('status')}, Severity: {d.get('severity', 'info')})\n"
        
        subdo_sample = ""
        for s in subdomains[:20]:
            name = s.get('subdomain', s) if isinstance(s, dict) else s
            subdo_sample += f"  - {name}\n"
        
        prompt = f"""You are a Senior Penetration Tester and Security Analyst. Analyze the following reconnaissance scan results for target: {target}

=== SCAN RESULTS ===

1. WAF DETECTION:
   Status: {"DETECTED - " + waf.get('waf_name', 'Unknown') if waf.get('detected') else "NOT DETECTED (VULNERABLE)"}
   Vendor: {waf.get('waf_vendor', 'N/A')}

2. OPEN PORTS & SERVICES ({len(ports)} found):
{ports_detail if ports_detail else "   No ports scanned or found."}

3. CMS DETECTION:
   Detected: {cms.get('cms_name', 'None')} {cms.get('cms_version', '')}
   Confidence: {cms.get('confidence', 'N/A')}

4. TECHNOLOGY STACK:
{tech_detail if tech_detail else "   No technologies identified."}

5. SUBDOMAINS ({subdomain_count} discovered):
{subdo_sample if subdo_sample else "   None found."}

6. DIRECTORIES/ENDPOINTS:
{dirs_detail if dirs_detail else "   None found."}

=== YOUR TASK ===

Provide a comprehensive security analysis with the following structure:

1. EXECUTIVE SUMMARY (2-3 paragraphs):
   - Overall security posture assessment
   - Critical risks and immediate concerns
   - Attack surface evaluation

2. KEY FINDINGS TABLE:
   For each notable finding, provide JSON array format:
   [
     {{"finding": "Description", "severity": "Critical/High/Medium/Low", "recommendation": "Action to take", "cve": "CVE-XXXX-XXXX or N/A"}}
   ]
   
   Focus on:
   - Services with known CVEs based on version numbers
   - Exposed administrative endpoints
   - Outdated software versions
   - Missing security controls (no WAF, etc)
   - Interesting subdomains (admin, dev, staging, api, etc)
   - Sensitive directories found

IMPORTANT:
- For any software version found, research known CVEs for that version
- Be specific about which endpoints/subdomains need investigation
- Prioritize findings by actual risk
- Keep summary professional and actionable

Output format (use exactly this structure):
---SUMMARY---
[Your executive summary here]
---FINDINGS---
[JSON array of findings]
"""
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        raw_text = response.text
        
        # Parse response
        summary = ""
        findings = []
        
        if "---SUMMARY---" in raw_text and "---FINDINGS---" in raw_text:
            parts = raw_text.split("---FINDINGS---")
            summary = parts[0].replace("---SUMMARY---", "").strip()
            
            if len(parts) > 1:
                findings_text = parts[1].strip()
                # Try to extract JSON array
                try:
                    # Find JSON array in the text
                    start = findings_text.find('[')
                    end = findings_text.rfind(']') + 1
                    if start != -1 and end > start:
                        json_str = findings_text[start:end]
                        findings = json.loads(json_str)
                except:
                    findings = []
        else:
            # Fallback: use entire response as summary
            summary = raw_text.replace('*', '').strip()
        
        return {
            "summary": summary,
            "findings": findings
        }
        
    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        return {
            "summary": generate_basic_summary(scan_data) + f" (AI Generation Failed: {str(e)[:50]})",
            "findings": []
        }


def generate_basic_summary(scan_data: dict) -> str:
    """Generate a basic summary without AI."""
    results = scan_data.get('results', {})
    parts = []
    
    # Check WAF
    waf = results.get('waf', {})
    if waf.get('detected'):
        parts.append(f"Target is protected by {waf.get('waf_name', 'WAF')}.")
    else:
        parts.append("Target appears UNPROTECTED (No WAF detected).")
    
    # Check Ports
    port = results.get('port', {})
    open_ports = port.get('open_ports', [])
    high_risk_ports = [p for p in open_ports if p.get('risk') == 'high']
    if high_risk_ports:
        parts.append(f"CRITICAL: Found {len(high_risk_ports)} high-risk open ports.")
    else:
        parts.append(f"Confirmed {len(open_ports)} exposed services.")
        
    # Check Subdomains
    subdo = results.get('subdo', {})
    count = subdo.get('count', 0)
    parts.append(f"Mapped {count} subdomains.")
        
    return " ".join(parts)

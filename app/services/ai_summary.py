"""
AI Summary Service - Concise Analysis
Generates brief executive summary with focus on findings and CVE table.
"""
from google import genai
import json

def generate_ai_summary(scan_data: dict, api_key: str = None) -> dict:
    """
    Generates a concise executive summary with detailed findings.
    Returns dict with 'summary' and 'findings' (list for table).
    """
    if not api_key:
        return {
            "summary": generate_basic_summary(scan_data),
            "findings": []
        }
        
    try:
        client = genai.Client(api_key=api_key)
        
        target = scan_data.get('target', 'Unknown')
        results = scan_data.get('results', {})
        
        waf = results.get('waf', {})
        ports = results.get('port', {}).get('open_ports', [])
        subdomains = results.get('subdo', {}).get('subdomains', [])
        subdomain_count = results.get('subdo', {}).get('count', 0)
        cms = results.get('cms', {})
        tech = results.get('tech', {}).get('technologies', [])
        directories = results.get('dir', {}).get('directories', [])
        
        # Build context
        ports_info = ", ".join([f"{p.get('port')}/{p.get('service','?')} v{p.get('version','?')}" for p in ports[:10]])
        tech_info = ", ".join([t.get('name', t) if isinstance(t, dict) else t for t in tech[:8]])
        dirs_info = ", ".join([d.get('path','') for d in directories[:8]])
        subdo_info = ", ".join([s.get('subdomain', s) if isinstance(s, dict) else s for s in subdomains[:15]])
        
        prompt = f"""You are a security analyst. Analyze this scan of {target}:

WAF: {"Protected by " + waf.get('waf_name', 'Unknown') if waf.get('detected') else "UNPROTECTED"}
Ports ({len(ports)}): {ports_info or 'None'}
CMS: {cms.get('cms_name', 'None')} {cms.get('cms_version', '')}
Tech: {tech_info or 'None'}
Subdomains ({subdomain_count}): {subdo_info or 'None'}
Directories: {dirs_info or 'None'}

Provide:

1. SUMMARY (3-4 sentences MAX): State overall risk level, main concerns, and action priority. Be direct.

2. FINDINGS (JSON array, focus on actionable items):
[
  {{"finding": "Brief description", "severity": "Critical/High/Medium/Low", "cve": "CVE-XXXX-XXXX", "action": "What to do"}}
]

Include:
- Known CVEs for detected software versions
- Interesting subdomains (admin, api, dev, staging, test, backup)
- Exposed sensitive directories
- Missing security controls
- Outdated software

Keep findings SHORT. Max 10 items. Use N/A if no CVE.

Format exactly:
---SUMMARY---
[brief summary]
---FINDINGS---
[json array]"""
        
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=prompt
        )
        
        raw_text = response.text
        
        summary = ""
        findings = []
        
        if "---SUMMARY---" in raw_text and "---FINDINGS---" in raw_text:
            parts = raw_text.split("---FINDINGS---")
            summary = parts[0].replace("---SUMMARY---", "").strip()[:500]  # Limit length
            
            if len(parts) > 1:
                try:
                    start = parts[1].find('[')
                    end = parts[1].rfind(']') + 1
                    if start != -1 and end > start:
                        findings = json.loads(parts[1][start:end])
                except:
                    pass
        else:
            summary = raw_text[:400]
        
        return {"summary": summary, "findings": findings}
        
    except Exception as e:
        return {
            "summary": generate_basic_summary(scan_data),
            "findings": []
        }


def generate_basic_summary(scan_data: dict) -> str:
    """Generate basic summary without AI."""
    results = scan_data.get('results', {})
    waf = results.get('waf', {})
    ports = results.get('port', {}).get('open_ports', [])
    subdo = results.get('subdo', {}).get('count', 0)
    
    status = "Protected" if waf.get('detected') else "Unprotected"
    risk_ports = len([p for p in ports if p.get('risk') == 'high'])
    
    return f"Target is {status}. Found {len(ports)} ports ({risk_ports} high-risk), {subdo} subdomains."

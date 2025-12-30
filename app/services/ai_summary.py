"""
AI Summary Service
Generates professional executive summaries using Google Gemini API.
"""
import google.generativeai as genai

def generate_ai_summary(scan_data: dict, api_key: str = None) -> str:
    """
    Generates an executive summary using Gemini API.
    Falls back to basic summary if API fails.
    """
    if not api_key:
        return generate_basic_summary(scan_data)
        
    try:
        genai.configure(api_key=api_key)
        model = genai.GenerativeModel('gemini-pro')
        
        # Prepare context
        target = scan_data.get('target', 'Unknown')
        waf = scan_data.get('results', {}).get('waf', {})
        ports = scan_data.get('results', {}).get('port', {}).get('open_ports', [])
        subdomains = scan_data.get('results', {}).get('subdo', {}).get('count', 0)
        cms = scan_data.get('results', {}).get('cms', {})
        
        prompt = f"""
        Act as a Senior Cybersecurity Consultant. Write a concise, professional executive summary (max 150 words) for a security reconnaissance report on target: {target}.
        
        Key Findings:
        - WAF Status: {"Protected (" + waf.get('waf_name', 'Unknown') + ")" if waf.get('detected') else "Unprotected (High Risk)"}
        - Open Ports: {len(ports)} found ({', '.join([str(p.get('port')) + '/' + p.get('service', 'unknown') for p in ports[:5]])}...)
        - Subdomains: {subdomains} discovered
        - CMS: {cms.get('cms_name', 'None Detected')} {cms.get('cms_version', '')}
        
        Tone: Professional, urgent if risks found, objective.
        Focus on business risk and security posture. Do not use markdown, just plain text paragraphs.
        """
        
        response = model.generate_content(prompt)
        return response.text.replace('*', '')  # Clean up any potential markdown
        
    except Exception as e:
        print(f"Gemini API Error: {str(e)}")
        return generate_basic_summary(scan_data) + f" (AI Generation Failed: {str(e)[:50]})"


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

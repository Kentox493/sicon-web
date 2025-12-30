"""
PDF Report Generator Service - Dark Theme

Generates beautiful dark-themed PDF reports from scan data.
Features:
- S1C0N Design System (Black & WhatsApp Green)
- Custom Logo Integration
- Structured Data Tables
- Security Summaries
"""

import os
import io
import math
from datetime import datetime
from typing import Dict, Any, Optional, List
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT
from reportlab.pdfgen import canvas

# S1C0N Color Palette
SICON_BLACK = colors.Color(0/255, 0/255, 0/255)
SICON_BG_BLACK = colors.Color(5/255, 5/255, 5/255)  # Slightly lighter for contrast if needed, but keeping pure black request
SICON_GREEN = colors.Color(37/255, 211/255, 102/255)
SICON_DARK_GREEN = colors.Color(12/255, 26/255, 16/255)
SICON_GRAY = colors.Color(156/255, 163/255, 175/255)
SICON_WHITE = colors.Color(255/255, 255/255, 255/255)
SICON_LIGHT_GRAY = colors.Color(229/255, 231/255, 235/255)

# Path configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOGO_PATH = os.path.join(BASE_DIR, "web", "src", "assets", "logo.png")

def add_background(canvas, doc):
    """Draws the dark background on every page."""
    canvas.saveState()
    canvas.setFillColor(SICON_BLACK)
    canvas.rect(0, 0, A4[0], A4[1], fill=1)
    
    # Add subtle green border line at top
    canvas.setStrokeColor(SICON_GREEN)
    canvas.setLineWidth(2)
    canvas.line(0, A4[1] - 5, A4[0], A4[1] - 5)
    
    # Add footer watermarks or similar if needed
    canvas.restoreState()

def create_styles():
    """Create custom dark-theme paragraph styles."""
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='SiconTitle',
        parent=styles['Title'],
        fontSize=24,
        textColor=SICON_WHITE,
        spaceAfter=10,
        alignment=TA_CENTER,
    ))
    
    styles.add(ParagraphStyle(
        name='SiconSubtitle',
        parent=styles['Heading2'],
        fontSize=14,
        textColor=SICON_GREEN,
        spaceAfter=20,
        alignment=TA_CENTER,
    ))
    
    styles.add(ParagraphStyle(
        name='SiconHeading',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=SICON_GREEN,
        spaceBefore=15,
        spaceAfter=10,
    ))
    
    styles.add(ParagraphStyle(
        name='SiconBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor=SICON_LIGHT_GRAY,
        spaceAfter=6,
        leading=14,
    ))
    
    styles.add(ParagraphStyle(
        name='SiconSmall',
        parent=styles['Normal'],
        fontSize=8,
        textColor=SICON_GRAY,
    ))
    
    styles.add(ParagraphStyle(
        name='SiconHighlight',
        parent=styles['Normal'],
        fontSize=10,
        textColor=SICON_GREEN,
        backColor=SICON_DARK_GREEN,
    ))
    
    return styles

def generate_scan_report(scan_data: Dict[str, Any], user_data: Dict[str, Any]) -> bytes:
    """Generate PDF report."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=20*mm,
        leftMargin=20*mm,
        topMargin=20*mm,
        bottomMargin=20*mm
    )
    
    styles = create_styles()
    story = []
    
    # --- HEADER ---
    try:
        if os.path.exists(LOGO_PATH):
            # Resize logic for logo
            img = Image(LOGO_PATH, width=1.5*inch, height=1.5*inch)
            img.hAlign = 'CENTER'
            story.append(img)
            story.append(Spacer(1, 10))
        else:
            story.append(Paragraph("S1C0N", styles['SiconTitle']))
    except Exception:
        story.append(Paragraph("S1C0N", styles['SiconTitle']))

    story.append(Paragraph("SECURITY ASSESSMENT REPORT", styles['SiconSubtitle']))
    story.append(HRFlowable(width="100%", thickness=1, color=SICON_GREEN, spaceBefore=5, spaceAfter=20))
    
    # --- SCAN INFO ---
    info_data = [
        ["TARGET", scan_data.get('target', 'N/A')],
        ["SCAN ID", f"#{scan_data.get('id', 'N/A')}"],
        ["DATE", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ["CLIENT", user_data.get('username', 'Unknown')],
    ]
    
    info_table = Table(info_data, colWidths=[100, 350])
    info_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (0, -1), SICON_GREEN),
        ('TEXTCOLOR', (1, 0), (1, -1), SICON_WHITE),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 20))
    
    # --- EXECUTIVE SUMMARY ---
    story.append(Paragraph("EXECUTIVE SUMMARY", styles['SiconHeading']))
    results = scan_data.get('results', {})
    summary = generate_summary(results)
    
    # Create a highlighted box for summary
    story.append(Table(
        [[Paragraph(summary, styles['SiconBody'])]],
        colWidths=[450],
        style=TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), SICON_DARK_GREEN),
            ('BOX', (0, 0), (-1, -1), 1, SICON_GREEN),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ])
    ))
    story.append(Spacer(1, 20))
    
    # --- RESULTS MODULES ---
    
    # 1. WAF
    if 'waf' in results:
        story.append(Paragraph("WAF DETECTION", styles['SiconHeading']))
        waf = results['waf']
        detected = waf.get('detected', False)
        
        waf_status = [
            ["Protection Status", "DETECTED" if detected else "NOT DETECTED"],
            ["WAF Name", waf.get('waf_name', 'None') or 'N/A'],
            ["Vendor", waf.get('waf_vendor', 'N/A') or 'N/A']
        ]
        
        t = Table(waf_status, colWidths=[150, 300])
        t.setStyle(get_dark_table_style(highlight_row=0 if detected else None))
        story.append(t)
        story.append(Spacer(1, 15))

    # 2. PORTS
    if 'port' in results:
        story.append(Paragraph("OPEN PORTS & SERVICES", styles['SiconHeading']))
        port_data = results['port']
        ports = port_data.get('open_ports', [])
        
        if ports:
            # Header
            data = [["PORT", "PROTOCOL", "SERVICE", "VERSION", "RISK"]]
            # Rows
            for p in ports:
                data.append([
                    str(p.get('port')),
                    p.get('protocol', 'tcp'),
                    p.get('service', 'unknown'),
                    p.get('version', '')[:25],
                    p.get('risk', 'low').upper()
                ])
            
            t = Table(data, colWidths=[50, 60, 80, 180, 80])
            t.setStyle(get_dark_table_style(header=True))
            story.append(t)
            
            # Risk legend
            story.append(Spacer(1, 5))
            if any(p.get('risk') == 'high' for p in ports):
                story.append(Paragraph("⚠️ High risk ports detected! Immediate attention recommended.", 
                                    ParagraphStyle('Warning', parent=styles['SiconBody'], textColor=colors.red)))
        else:
            story.append(Paragraph("No open ports found.", styles['SiconBody']))
        story.append(Spacer(1, 15))

    # 3. SUBDOMAINS - IMPROVED LAYOUT
    if 'subdo' in results:
        story.append(Paragraph("SUBDOMAIN ENUMERATION", styles['SiconHeading']))
        subdo = results['subdo']
        subdomains = subdo.get('subdomains', [])
        count = subdo.get('count', 0)
        
        story.append(Paragraph(f"Total Found: {count}", styles['SiconBody']))
        story.append(Spacer(1, 5))
        
        if subdomains:
            # Format subdomains into a 2-column grid for better readability
            # Filter just the names
            names = [s.get('subdomain', s) if isinstance(s, dict) else s for s in subdomains]
            
            # Chunk into pairs
            rows = []
            for i in range(0, len(names), 2):
                c1 = names[i]
                c2 = names[i+1] if i+1 < len(names) else ""
                rows.append([c1, c2])
            
            # Limit rows to avoid huge report
            if len(rows) > 50:
                rows = rows[:50]
                rows.append(["...", "..."])
            
            t = Table(rows, colWidths=[225, 225])
            t.setStyle(TableStyle([
                ('TEXTCOLOR', (0, 0), (-1, -1), SICON_LIGHT_GRAY),
                ('FONTNAME', (0, 0), (-1, -1), 'Courier'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 2),
                ('TOPPADDING', (0, 0), (-1, -1), 2),
                ('GRID', (0, 0), (-1, -1), 0.25, SICON_DARK_GREEN), # Subtle grid
                ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.1, 0.1, 0.1)), # Slightly lighter than black
            ]))
            story.append(t)
        else:
            story.append(Paragraph("No subdomains found.", styles['SiconBody']))
        story.append(Spacer(1, 15))

    # 4. CMS & TECH
    if 'cms' in results or 'tech' in results:
        story.append(Paragraph("TECHNOLOGY STACK", styles['SiconHeading']))
        
        tech_data = []
        
        # CMS
        if 'cms' in results:
            cms = results['cms']
            if cms.get('detected'):
                tech_data.append(["CMS", f"{cms.get('cms_name')} {cms.get('cms_version') or ''}"])
        
        # Tech
        if 'tech' in results:
            tech = results['tech']
            for t in tech.get('technologies', []):
                name = t.get('name', t) if isinstance(t, dict) else t
                cat = t.get('category', 'Technology') if isinstance(t, dict) else 'Technology'
                tech_data.append([cat.replace('_', ' ').title(), name])
        
        if tech_data:
            t = Table(tech_data, colWidths=[150, 300])
            t.setStyle(get_dark_table_style())
            story.append(t)
        else:
             story.append(Paragraph("No specific technologies identified.", styles['SiconBody']))

    # 5. DIRECTORIES
    if 'dir' in results:
        story.append(Paragraph("DIRECTORY SCAN", styles['SiconHeading']))
        dir_data = results['dir']
        dirs = dir_data.get('directories', [])
        
        if dirs:
            data = [["STATUS", "PATH", "SEVERITY"]]
            for d in dirs[:20]: # Limit for brevity
                status_code = d.get('status', 0)
                # Colorize status text
                s_text = str(status_code)
                severity = d.get('severity', 'info')
                
                data.append([s_text, d.get('path'), severity.upper()])
            
            t = Table(data, colWidths=[60, 300, 90])
            t.setStyle(get_dark_table_style(header=True))
            story.append(t)
        else:
            story.append(Paragraph("No interesting directories found.", styles['SiconBody']))

    # Footer
    story.append(Spacer(1, 30))
    story.append(HRFlowable(width="100%", thickness=1, color=SICON_GREEN))
    story.append(Paragraph("CONFIDENTIAL - Generated by S1C0N", styles['SiconSmall']))

    # Build with background
    doc.build(story, onFirstPage=add_background, onLaterPages=add_background)
    buffer.seek(0)
    return buffer.getvalue()


def get_dark_table_style(header=False, highlight_row=None):
    """Common table style for dark theme."""
    style = [
        ('TEXTCOLOR', (0, 0), (-1, -1), SICON_LIGHT_GRAY),
        ('GRID', (0, 0), (-1, -1), 0.5, SICON_GREEN),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
        ('TOPPADDING', (0, 0), (-1, -1), 6),
        ('BACKGROUND', (0, 0), (-1, -1), colors.Color(0.05, 0.05, 0.05)), # Very dark grey
    ]
    
    if header:
        style.extend([
            ('BACKGROUND', (0, 0), (-1, 0), SICON_GREEN), # Header row
            ('TEXTCOLOR', (0, 0), (-1, 0), SICON_BLACK),
            ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ])
    
    if highlight_row is not None:
         style.extend([
            ('TEXTCOLOR', (1, highlight_row), (1, highlight_row), SICON_GREEN),
            ('FONTNAME', (1, highlight_row), (1, highlight_row), 'Helvetica-Bold'),
        ])

    return TableStyle(style)

def generate_summary(results: Dict[str, Any]) -> str:
    """Generate executive summary."""
    parts = []
    
    # High level risk assessment
    risks = 0
    
    # Check WAF
    waf = results.get('waf', {})
    if waf.get('detected'):
        parts.append(f"Target is protected by {waf.get('waf_name', 'WAF')}.")
    else:
        parts.append("Target appears UNPROTECTED (No WAF detected).")
        risks += 1
    
    # Check Ports
    port = results.get('port', {})
    open_ports = port.get('open_ports', [])
    high_risk_ports = [p for p in open_ports if p.get('risk') == 'high']
    if high_risk_ports:
        parts.append(f"CRITICAL: Found {len(high_risk_ports)} high-risk open ports.")
        risks += 2
    else:
        parts.append(f"Found {len(open_ports)} open ports.")
        
    # Check Subdomains
    subdo = results.get('subdo', {})
    parts.append(f"Enumerated {subdo.get('count', 0)} subdomains.")
    
    # CMS
    cms = results.get('cms', {})
    if cms.get('detected'):
        parts.append(f"Running {cms.get('cms_name')}.")
        
    if risks >= 2:
        parts.append("OVERALL STATUS: HIGH RISK TARGET.")
    elif risks == 1:
        parts.append("OVERALL STATUS: MODERATE RISK.")
    else:
        parts.append("OVERALL STATUS: LOW RISK OBSERVED.")
        
    return " ".join(parts)

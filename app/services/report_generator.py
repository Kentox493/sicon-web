"""
PDF Report Generator Service - Neon Dark Theme

Generates professional, high-contrast dark-themed PDF reports from scan data.
Features:
- S1C0N Neon Design System (Black & Bright Neon Green)
- Default Size Logo (Esthetic)
- Tabular Data Layouts
- Professional Typography
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
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT, TA_JUSTIFY
from reportlab.pdfgen import canvas

# S1C0N Neon Palette
NEON_BLACK = colors.Color(0/255, 0/255, 0/255)         # Pure Black
NEON_GREEN = colors.Color(37/255, 211/255, 102/255)    # WhatsApp Green (Bright)
NEON_GLOW = colors.Color(37/255, 211/255, 102/255, alpha=0.3) # Transparent Green for glow effects
NEON_DARK_GREEN = colors.Color(6/255, 30/255, 15/255)  # Very dark green for row bands
NEON_WHITE = colors.Color(240/255, 255/255, 240/255)   # Off-white with green tint
NEON_GRAY = colors.Color(100/255, 100/255, 100/255)    # Dark Gray

# Path configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOGO_PATH = os.path.join(BASE_DIR, "web", "src", "assets", "logo.png")

def add_background(canvas, doc):
    """Draws the dark background on every page with neon borders."""
    canvas.saveState()
    # Fill Background
    canvas.setFillColor(NEON_BLACK)
    canvas.rect(0, 0, A4[0], A4[1], fill=1)
    
    # Neon Border
    canvas.setStrokeColor(NEON_GREEN)
    canvas.setLineWidth(1)
    margin = 10 * mm
    canvas.rect(margin, margin, A4[0] - 2*margin, A4[1] - 2*margin)
    
    # Corner Accents (Cyberpunk/Neon style)
    corner_len = 10 * mm
    canvas.setLineWidth(3)
    
    # Top Left
    canvas.line(margin, A4[1]-margin, margin + corner_len, A4[1]-margin)
    canvas.line(margin, A4[1]-margin, margin, A4[1]-margin - corner_len)
    
    # Top Right
    canvas.line(A4[0]-margin, A4[1]-margin, A4[0]-margin - corner_len, A4[1]-margin)
    canvas.line(A4[0]-margin, A4[1]-margin, A4[0]-margin, A4[1]-margin - corner_len)
    
    # Bottom Left
    canvas.line(margin, margin, margin + corner_len, margin)
    canvas.line(margin, margin, margin, margin + corner_len)
    
    # Bottom Right
    canvas.line(A4[0]-margin, margin, A4[0]-margin - corner_len, margin)
    canvas.line(A4[0]-margin, margin, A4[0]-margin, margin + corner_len)
    
    canvas.restoreState()

def create_styles():
    """Create custom neon dark-theme styles."""
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='NeonTitle',
        parent=styles['Title'],
        fontName='Helvetica-Bold',
        fontSize=24,
        textColor=NEON_WHITE,
        spaceAfter=10,
        alignment=TA_CENTER,
    ))
    
    styles.add(ParagraphStyle(
        name='NeonSubtitle',
        parent=styles['Heading2'],
        fontName='Helvetica',
        fontSize=14,
        textColor=NEON_GREEN,
        spaceAfter=25,
        alignment=TA_CENTER,
        leading=18,
    ))
    
    styles.add(ParagraphStyle(
        name='NeonHeading',
        parent=styles['Heading1'],
        fontName='Helvetica-Bold',
        fontSize=16,
        textColor=NEON_GREEN,
        spaceBefore=20,
        spaceAfter=15,
        borderPadding=5,
        borderWidth=0,
        borderColor=NEON_GREEN,
        borderRadius=2,
    ))
    
    styles.add(ParagraphStyle(
        name='NeonBody',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=10,
        textColor=NEON_WHITE,
        leading=14,
        spaceAfter=8,
    ))
    
    styles.add(ParagraphStyle(
        name='NeonSmall',
        parent=styles['Normal'],
        fontName='Courier',
        fontSize=8,
        textColor=NEON_GRAY,
        alignment=TA_CENTER,
    ))
    
    return styles

def generate_scan_report(scan_data: Dict[str, Any], user_data: Dict[str, Any]) -> bytes:
    """Generate Neon PDF report."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(
        buffer,
        pagesize=A4,
        rightMargin=25*mm,
        leftMargin=25*mm,
        topMargin=25*mm,
        bottomMargin=25*mm
    )
    
    styles = create_styles()
    story = []
    
    # --- LOGO & HEADER ---
    try:
        if os.path.exists(LOGO_PATH):
            # Use a reasonable default size, not too small
            # ~3 inches wide usually looks good on A4
            img = Image(LOGO_PATH, width=3*inch, height=1.5*inch, kind='proportional')
            img.hAlign = 'CENTER'
            story.append(img)
            story.append(Spacer(1, 15))
        else:
            story.append(Paragraph("S1C0N", styles['NeonTitle']))
    except Exception:
        story.append(Paragraph("S1C0N", styles['NeonTitle']))

    story.append(Paragraph("CYBER RECONNAISSANCE REPORT", styles['NeonSubtitle']))
    
    # --- SCAN PROPERTIES ---
    info_data = [
        ["TARGET ASSET", scan_data.get('target', 'N/A').upper()],
        ["SCAN REFERENCE", f"#{scan_data.get('id', 'N/A')}"],
        ["EXECUTION TIME", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
        ["OPERATOR", user_data.get('username', 'Unknown').upper()],
    ]
    
    info_table = Table(info_data, colWidths=[150, 300])
    info_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (0, -1), NEON_GREEN),
        ('TEXTCOLOR', (1, 0), (1, -1), NEON_WHITE),
        ('FONTNAME', (0, 0), (-1, -1), 'Courier-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, NEON_GREEN), # Green dividers
    ]))
    story.append(info_table)
    story.append(Spacer(1, 25))
    
    # --- EXECUTIVE SUMMARY BOX ---
    story.append(Paragraph("EXECUTIVE SUMMARY", styles['NeonHeading']))
    results = scan_data.get('results', {})
    summary = generate_summary(results)
    
    summary_table = Table(
        [[Paragraph(summary, styles['NeonBody'])]],
        colWidths=[450],
        style=TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), NEON_DARK_GREEN), # Dark green fill
            ('BOX', (0, 0), (-1, -1), 1, NEON_GREEN),         # Neon border
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ])
    )
    story.append(summary_table)
    story.append(Spacer(1, 25))
    
    # --- FINDINGS ---

    # 1. WAF
    if 'waf' in results:
        story.append(Paragraph("WAF PROTECTION", styles['NeonHeading']))
        waf = results['waf']
        detected = waf.get('detected', False)
        
        waf_status = [
            ["STATUS", "DETECTED" if detected else "NOT DETECTED"],
            ["WAF NAME", (waf.get('waf_name', 'None') or 'N/A').upper()],
            ["VENDOR", (waf.get('waf_vendor', 'N/A') or 'N/A').upper()]
        ]
        
        t = Table(waf_status, colWidths=[150, 300])
        t.setStyle(get_neon_table_style())
        story.append(t)
        story.append(Spacer(1, 20))

    # 2. PORTS
    if 'port' in results:
        story.append(Paragraph("OPEN PORTS", styles['NeonHeading']))
        port_data = results['port']
        ports = port_data.get('open_ports', [])
        
        if ports:
            # Table Header
            data = [["PORT", "PROTO", "SERVICE", "VERSION", "RISK"]]
            # Rows
            for p in ports:
                data.append([
                    str(p.get('port')),
                    p.get('protocol', 'tcp'),
                    p.get('service', 'unknown'),
                    p.get('version', '')[:20],
                    p.get('risk', 'low').upper()
                ])
            
            t = Table(data, colWidths=[50, 50, 80, 190, 80])
            t.setStyle(get_neon_table_style(header=True))
            story.append(t)
        else:
            story.append(Paragraph("\u2714 No open ports detected.", styles['NeonBody']))
        story.append(Spacer(1, 20))

    # 3. SUBDOMAINS - TABLE LAYOUT
    if 'subdo' in results:
        story.append(Paragraph("SUBDOMAINS", styles['NeonHeading']))
        subdo = results['subdo']
        subdomains = subdo.get('subdomains', [])
        count = subdo.get('count', 0)
        
        story.append(Paragraph(f"Discoveries: {count}", styles['NeonBody']))
        story.append(Spacer(1, 5))
        
        if subdomains:
            # Create a clean table for subdomains instead of a massive grid
            # Columns: #, Subdomain, Type
            data = [["#", "SUBDOMAIN", "TYPE"]]
            
            for i, s in enumerate(subdomains[:60]): # Limit to first 60 to prevent PDF overflow issues
                name = s.get('subdomain', s) if isinstance(s, dict) else s
                stype = s.get('type', 'regular') if isinstance(s, dict) else 'regular'
                data.append([str(i+1), name, stype.upper()])
            
            if len(subdomains) > 60:
                data.append(["...", f"... and {len(subdomains)-60} more", "..."])

            t = Table(data, colWidths=[40, 310, 100])
            t.setStyle(get_neon_table_style(header=True))
            story.append(t)
        else:
            story.append(Paragraph("\u2716 No subdomains found.", styles['NeonBody']))
        story.append(Spacer(1, 20))

    # 4. TECH STACK
    if 'cms' in results or 'tech' in results:
        story.append(Paragraph("TECHNOLOGIES", styles['NeonHeading']))
        
        tech_data = [["CATEGORY", "TECHNOLOGY"]]
        
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
                cat = t.get('category', 'General') if isinstance(t, dict) else 'General'
                tech_data.append([cat.replace('_', ' ').upper(), name])
        
        if len(tech_data) > 1:
            t = Table(tech_data, colWidths=[150, 300])
            t.setStyle(get_neon_table_style(header=True))
            story.append(t)
        else:
             story.append(Paragraph("No technologies identified.", styles['NeonBody']))

    # 5. DIRECTORIES
    if 'dir' in results:
        story.append(Paragraph("DIRECTORIES", styles['NeonHeading']))
        dir_data = results['dir']
        dirs = dir_data.get('directories', [])
        
        if dirs:
            data = [["CODE", "PATH", "SEVERITY"]]
            for d in dirs[:25]: # Limit
                status_code = str(d.get('status', 0))
                severity = d.get('severity', 'info').upper()
                data.append([status_code, d.get('path'), severity])
            
            t = Table(data, colWidths=[50, 300, 100])
            t.setStyle(get_neon_table_style(header=True))
            story.append(t)
        else:
            story.append(Paragraph("No accessible directories.", styles['NeonBody']))

    # Footer
    story.append(Spacer(1, 40))
    story.append(HRFlowable(width="100%", thickness=1, color=NEON_GREEN))
    story.append(Paragraph(f"S1C0N RECONNAISSANCE PLATFORM | {datetime.now().strftime('%Y')}", styles['NeonSmall']))

    # Build PDF
    doc.build(story, onFirstPage=add_background, onLaterPages=add_background)
    buffer.seek(0)
    return buffer.getvalue()


def get_neon_table_style(header=False):
    """Neon table style."""
    style = [
        ('TEXTCOLOR', (0, 0), (-1, -1), NEON_WHITE),
        ('GRID', (0, 0), (-1, -1), 0.5, NEON_GREEN),
        ('FONTNAME', (0, 0), (-1, -1), 'Courier'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BACKGROUND', (0, 0), (-1, -1), NEON_BLACK),
    ]
    
    if header:
        style.extend([
            ('BACKGROUND', (0, 0), (-1, 0), NEON_GREEN), # Header Row
            ('TEXTCOLOR', (0, 0), (-1, 0), NEON_BLACK),
            ('FONTNAME', (0, 0), (-1, 0), 'Courier-Bold'),
        ])
        
    return TableStyle(style)

def generate_summary(results: Dict[str, Any]) -> str:
    """Generate professional executive summary."""
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

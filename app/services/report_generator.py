"""
PDF Report Generator Service - Neon Dark Theme with Optional AI & Data Viz

Features:
- S1C0N Neon Design System (Black & Bright Neon Green)
- Custom Logo Integration
- Optional AI-Powered Executive Summary (Gemini)
- Data Visualization Charts (Matplotlib)
"""

import os
import io
from datetime import datetime
from typing import Dict, Any, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# Import services
from app.services.ai_summary import generate_ai_summary, generate_basic_summary
from app.services.chart_generator import create_severity_pie_chart, create_findings_bar_chart

# S1C0N Neon Palette
NEON_BLACK = colors.Color(0/255, 0/255, 0/255)
NEON_GREEN = colors.Color(37/255, 211/255, 102/255)
NEON_DARK_GREEN = colors.Color(6/255, 30/255, 15/255)
NEON_WHITE = colors.Color(240/255, 255/255, 240/255)
NEON_GRAY = colors.Color(100/255, 100/255, 100/255)

# Path configuration
BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOGO_PATH = os.path.join(BASE_DIR, "web", "src", "assets", "logo.png")


def add_background(canvas, doc):
    """Draws the dark background on every page with neon borders."""
    canvas.saveState()
    canvas.setFillColor(NEON_BLACK)
    canvas.rect(0, 0, A4[0], A4[1], fill=1)
    
    canvas.setStrokeColor(NEON_GREEN)
    canvas.setLineWidth(1)
    margin = 10 * mm
    canvas.rect(margin, margin, A4[0] - 2*margin, A4[1] - 2*margin)
    
    corner_len = 10 * mm
    canvas.setLineWidth(3)
    canvas.line(margin, A4[1]-margin, margin + corner_len, A4[1]-margin)
    canvas.line(margin, A4[1]-margin, margin, A4[1]-margin - corner_len)
    canvas.line(A4[0]-margin, A4[1]-margin, A4[0]-margin - corner_len, A4[1]-margin)
    canvas.line(A4[0]-margin, A4[1]-margin, A4[0]-margin, A4[1]-margin - corner_len)
    canvas.line(margin, margin, margin + corner_len, margin)
    canvas.line(margin, margin, margin, margin + corner_len)
    canvas.line(A4[0]-margin, margin, A4[0]-margin - corner_len, margin)
    canvas.line(A4[0]-margin, margin, A4[0]-margin, margin + corner_len)
    canvas.restoreState()


def create_styles():
    """Create custom neon dark-theme styles."""
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle('NeonTitle', parent=styles['Title'], fontName='Helvetica-Bold',
        fontSize=24, textColor=NEON_WHITE, spaceAfter=10, alignment=TA_CENTER))
    styles.add(ParagraphStyle('NeonSubtitle', parent=styles['Heading2'], fontName='Helvetica',
        fontSize=14, textColor=NEON_GREEN, spaceAfter=25, alignment=TA_CENTER, leading=18))
    styles.add(ParagraphStyle('NeonHeading', parent=styles['Heading1'], fontName='Helvetica-Bold',
        fontSize=16, textColor=NEON_GREEN, spaceBefore=20, spaceAfter=15))
    styles.add(ParagraphStyle('NeonBody', parent=styles['Normal'], fontName='Courier',
        fontSize=10, textColor=NEON_WHITE, leading=14, spaceAfter=8))
    styles.add(ParagraphStyle('NeonSmall', parent=styles['Normal'], fontName='Courier',
        fontSize=8, textColor=NEON_GRAY, alignment=TA_CENTER))
    
    return styles


def generate_scan_report(scan_data: Dict[str, Any], user_data: Dict[str, Any], 
                         use_ai: bool = False, api_key: str = None) -> bytes:
    """Generate Neon PDF report with optional AI Summary & Charts."""
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
        rightMargin=25*mm, leftMargin=25*mm, topMargin=25*mm, bottomMargin=25*mm)
    
    styles = create_styles()
    story = []
    
    # --- LOGO & HEADER ---
    try:
        if os.path.exists(LOGO_PATH):
            img = Image(LOGO_PATH, width=3*inch, height=1.5*inch, kind='proportional')
            img.hAlign = 'CENTER'
            story.append(img)
            story.append(Spacer(1, 15))
        else:
            story.append(Paragraph("S1C0N", styles['NeonTitle']))
    except:
        story.append(Paragraph("S1C0N", styles['NeonTitle']))

    report_type = "AI-ENHANCED" if use_ai else "STANDARD"
    story.append(Paragraph(f"CYBER RECONNAISSANCE REPORT ({report_type})", styles['NeonSubtitle']))
    
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
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, NEON_GREEN),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 25))
    
    # --- EXECUTIVE SUMMARY ---
    summary_label = "EXECUTIVE SUMMARY (AI ENHANCED)" if use_ai else "EXECUTIVE SUMMARY"
    story.append(Paragraph(summary_label, styles['NeonHeading']))
    
    # Generate Summary
    if use_ai and api_key:
        summary_text = generate_ai_summary(scan_data, api_key)
    else:
        summary_text = generate_basic_summary(scan_data)
    
    summary_table = Table(
        [[Paragraph(summary_text, styles['NeonBody'])]],
        colWidths=[450],
        style=TableStyle([
            ('BACKGROUND', (0, 0), (-1, -1), NEON_DARK_GREEN),
            ('BOX', (0, 0), (-1, -1), 1, NEON_GREEN),
            ('LEFTPADDING', (0, 0), (-1, -1), 15),
            ('RIGHTPADDING', (0, 0), (-1, -1), 15),
            ('TOPPADDING', (0, 0), (-1, -1), 15),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 15),
        ])
    )
    story.append(summary_table)
    story.append(Spacer(1, 25))
    
    # --- DATA VISUALIZATION ---
    story.append(Paragraph("DATA VISUALIZATION", styles['NeonHeading']))
    
    try:
        pie_buf = create_severity_pie_chart(scan_data)
        bar_buf = create_findings_bar_chart(scan_data)
        
        chart_img1 = Image(pie_buf, width=3*inch, height=2*inch)
        chart_img2 = Image(bar_buf, width=3*inch, height=1.5*inch)
        
        chart_table = Table([[chart_img1, chart_img2]], colWidths=[225, 225])
        chart_table.setStyle(TableStyle([
            ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
            ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ]))
        story.append(chart_table)
        story.append(Spacer(1, 25))
    except Exception as e:
        story.append(Paragraph(f"Charts could not be generated: {str(e)[:50]}", styles['NeonBody']))

    # --- FINDINGS ---
    results = scan_data.get('results', {})
    
    # WAF
    if 'waf' in results:
        story.append(Paragraph("WAF PROTECTION", styles['NeonHeading']))
        waf = results['waf']
        t = Table([
            ["STATUS", "DETECTED" if waf.get('detected') else "NOT DETECTED"],
            ["WAF NAME", (waf.get('waf_name') or 'N/A').upper()],
            ["VENDOR", (waf.get('waf_vendor') or 'N/A').upper()]
        ], colWidths=[150, 300])
        t.setStyle(get_neon_table_style())
        story.append(t)
        story.append(Spacer(1, 20))

    # PORTS
    if 'port' in results:
        story.append(Paragraph("OPEN PORTS", styles['NeonHeading']))
        ports = results['port'].get('open_ports', [])
        if ports:
            data = [["PORT", "PROTO", "SERVICE", "VERSION", "RISK"]]
            for p in ports:
                data.append([str(p.get('port')), p.get('protocol', 'tcp'), 
                    p.get('service', 'unknown'), p.get('version', '')[:20], p.get('risk', 'low').upper()])
            t = Table(data, colWidths=[50, 50, 80, 190, 80])
            t.setStyle(get_neon_table_style(header=True))
            story.append(t)
        else:
            story.append(Paragraph("No open ports detected.", styles['NeonBody']))
        story.append(Spacer(1, 20))

    # SUBDOMAINS
    if 'subdo' in results:
        story.append(Paragraph("SUBDOMAINS", styles['NeonHeading']))
        subdomains = results['subdo'].get('subdomains', [])
        count = results['subdo'].get('count', 0)
        story.append(Paragraph(f"Discoveries: {count}", styles['NeonBody']))
        if subdomains:
            data = [["#", "SUBDOMAIN", "TYPE"]]
            for i, s in enumerate(subdomains[:60]):
                name = s.get('subdomain', s) if isinstance(s, dict) else s
                stype = s.get('type', 'regular') if isinstance(s, dict) else 'regular'
                data.append([str(i+1), name, stype.upper()])
            if len(subdomains) > 60:
                data.append(["...", f"... and {len(subdomains)-60} more", "..."])
            t = Table(data, colWidths=[40, 310, 100])
            t.setStyle(get_neon_table_style(header=True))
            story.append(t)
        story.append(Spacer(1, 20))

    # TECH
    if 'cms' in results or 'tech' in results:
        story.append(Paragraph("TECHNOLOGIES", styles['NeonHeading']))
        tech_data = [["CATEGORY", "TECHNOLOGY"]]
        if 'cms' in results and results['cms'].get('detected'):
            cms = results['cms']
            tech_data.append(["CMS", f"{cms.get('cms_name')} {cms.get('cms_version') or ''}"])
        if 'tech' in results:
            for tech in results['tech'].get('technologies', []):
                name = tech.get('name', tech) if isinstance(tech, dict) else tech
                cat = tech.get('category', 'General') if isinstance(tech, dict) else 'General'
                tech_data.append([cat.replace('_', ' ').upper(), name])
        if len(tech_data) > 1:
            t = Table(tech_data, colWidths=[150, 300])
            t.setStyle(get_neon_table_style(header=True))
            story.append(t)

    # Footer
    story.append(Spacer(1, 40))
    story.append(HRFlowable(width="100%", thickness=1, color=NEON_GREEN))
    story.append(Paragraph(f"S1C0N RECONNAISSANCE PLATFORM | {datetime.now().strftime('%Y')}", styles['NeonSmall']))

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
            ('BACKGROUND', (0, 0), (-1, 0), NEON_GREEN),
            ('TEXTCOLOR', (0, 0), (-1, 0), NEON_BLACK),
            ('FONTNAME', (0, 0), (-1, 0), 'Courier-Bold'),
        ])
    return TableStyle(style)

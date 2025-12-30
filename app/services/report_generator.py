"""
PDF Report Generator Service

Generates beautiful PDF reports from scan data using reportlab.
Uses S1C0N color palette: Black (#000000) and WhatsApp Green (#25D366).
"""

import os
import io
from datetime import datetime
from typing import Dict, Any, Optional
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT

# S1C0N Color Palette
SICON_BLACK = colors.Color(0, 0, 0)
SICON_GREEN = colors.Color(37/255, 211/255, 102/255)
SICON_DARK_GREEN = colors.Color(12/255, 26/255, 16/255)
SICON_GRAY = colors.Color(156/255, 163/255, 175/255)


def create_styles():
    """Create custom paragraph styles."""
    styles = getSampleStyleSheet()
    
    styles.add(ParagraphStyle(
        name='SiconTitle',
        parent=styles['Title'],
        fontSize=28,
        textColor=SICON_GREEN,
        spaceAfter=20,
        alignment=TA_CENTER,
    ))
    
    styles.add(ParagraphStyle(
        name='SiconHeading',
        parent=styles['Heading1'],
        fontSize=16,
        textColor=SICON_GREEN,
        spaceBefore=20,
        spaceAfter=10,
        borderWidth=0,
        borderPadding=0,
    ))
    
    styles.add(ParagraphStyle(
        name='SiconSubheading',
        parent=styles['Heading2'],
        fontSize=12,
        textColor=SICON_GRAY,
        spaceBefore=10,
        spaceAfter=5,
    ))
    
    styles.add(ParagraphStyle(
        name='SiconBody',
        parent=styles['Normal'],
        fontSize=10,
        textColor=colors.black,
        spaceAfter=5,
    ))
    
    styles.add(ParagraphStyle(
        name='SiconCode',
        parent=styles['Code'],
        fontSize=9,
        textColor=colors.black,
        backColor=colors.Color(240/255, 240/255, 240/255),
    ))
    
    return styles


def generate_scan_report(scan_data: Dict[str, Any], user_data: Dict[str, Any]) -> bytes:
    """
    Generate a PDF report from scan data.
    
    Args:
        scan_data: The scan object with results
        user_data: The user who requested the scan
    
    Returns:
        PDF file as bytes
    """
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
    
    # Header
    story.append(Paragraph("S1C0N", styles['SiconTitle']))
    story.append(Paragraph("Security Reconnaissance Report", styles['SiconSubheading']))
    story.append(Spacer(1, 20))
    
    # Horizontal line
    story.append(HRFlowable(width="100%", thickness=2, color=SICON_GREEN, spaceBefore=10, spaceAfter=20))
    
    # Scan Information Table
    scan_info = [
        ["Report ID", f"#{scan_data.get('id', 'N/A')}"],
        ["Target", scan_data.get('target', 'N/A')],
        ["Scan Type", scan_data.get('scan_type', 'full').capitalize()],
        ["Status", scan_data.get('status', 'N/A').upper()],
        ["Requested By", user_data.get('username', 'Unknown')],
        ["Started At", format_datetime(scan_data.get('started_at'))],
        ["Completed At", format_datetime(scan_data.get('completed_at'))],
        ["Generated At", datetime.now().strftime("%Y-%m-%d %H:%M:%S")],
    ]
    
    info_table = Table(scan_info, colWidths=[120, 350])
    info_table.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.Color(240/255, 240/255, 240/255)),
        ('TEXTCOLOR', (0, 0), (0, -1), colors.black),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('ALIGN', (0, 0), (0, -1), 'LEFT'),
        ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 30))
    
    # Executive Summary
    story.append(Paragraph("📋 Executive Summary", styles['SiconHeading']))
    story.append(HRFlowable(width="100%", thickness=1, color=SICON_GREEN, spaceAfter=10))
    
    results = scan_data.get('results', {})
    summary = generate_summary(results)
    story.append(Paragraph(summary, styles['SiconBody']))
    story.append(Spacer(1, 20))
    
    # WAF Detection Results
    if 'waf' in results:
        story.append(Paragraph("🛡️ WAF Detection", styles['SiconHeading']))
        story.append(HRFlowable(width="100%", thickness=1, color=SICON_GREEN, spaceAfter=10))
        waf = results['waf']
        
        waf_data = [
            ["Status", "Protected" if waf.get('detected') else "Not Protected"],
            ["WAF Name", waf.get('waf_name', 'None') or 'None'],
            ["Vendor", waf.get('waf_vendor', 'N/A') or 'N/A'],
        ]
        waf_table = Table(waf_data, colWidths=[120, 350])
        waf_table.setStyle(get_table_style(waf.get('detected')))
        story.append(waf_table)
        story.append(Spacer(1, 20))
    
    # Port Scan Results
    if 'port' in results:
        story.append(Paragraph("🔌 Port Scan Results", styles['SiconHeading']))
        story.append(HRFlowable(width="100%", thickness=1, color=SICON_GREEN, spaceAfter=10))
        port_data = results['port']
        
        open_ports = port_data.get('open_ports', [])
        if open_ports:
            port_table_data = [["Port", "Protocol", "Service", "Version", "Risk"]]
            for p in open_ports[:20]:  # Limit to 20
                port_table_data.append([
                    str(p.get('port', '')),
                    p.get('protocol', 'tcp'),
                    p.get('service', 'unknown'),
                    p.get('version', '')[:30],
                    p.get('risk', 'low').upper()
                ])
            
            port_table = Table(port_table_data, colWidths=[60, 60, 80, 180, 80])
            port_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), SICON_GREEN),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('ALIGN', (0, 0), (-1, -1), 'LEFT'),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 6),
                ('TOPPADDING', (0, 0), (-1, -1), 6),
                ('ROWBACKGROUNDS', (0, 1), (-1, -1), [colors.white, colors.Color(245/255, 245/255, 245/255)]),
            ]))
            story.append(port_table)
        else:
            story.append(Paragraph("No open ports detected.", styles['SiconBody']))
        story.append(Spacer(1, 20))
    
    # Subdomain Results
    if 'subdo' in results:
        story.append(Paragraph("🌐 Subdomain Enumeration", styles['SiconHeading']))
        story.append(HRFlowable(width="100%", thickness=1, color=SICON_GREEN, spaceAfter=10))
        subdo_data = results['subdo']
        
        story.append(Paragraph(f"Total Subdomains Found: <b>{subdo_data.get('count', 0)}</b>", styles['SiconBody']))
        story.append(Spacer(1, 5))
        
        subdomains = subdo_data.get('subdomains', [])
        if subdomains:
            # Display as a compact list
            sub_text = ", ".join([s.get('subdomain', s) if isinstance(s, dict) else s for s in subdomains[:30]])
            story.append(Paragraph(f"<font size=8>{sub_text}</font>", styles['SiconBody']))
        story.append(Spacer(1, 20))
    
    # CMS Detection
    if 'cms' in results:
        story.append(Paragraph("📦 CMS Detection", styles['SiconHeading']))
        story.append(HRFlowable(width="100%", thickness=1, color=SICON_GREEN, spaceAfter=10))
        cms = results['cms']
        
        cms_info = [
            ["CMS Detected", "Yes" if cms.get('detected') else "No"],
            ["CMS Name", cms.get('cms_name', 'None') or 'None'],
            ["Version", cms.get('cms_version', 'Unknown') or 'Unknown'],
            ["Confidence", (cms.get('confidence', 'N/A') or 'N/A').upper()],
        ]
        cms_table = Table(cms_info, colWidths=[120, 350])
        cms_table.setStyle(get_table_style(cms.get('detected')))
        story.append(cms_table)
        story.append(Spacer(1, 20))
    
    # Technology Stack
    if 'tech' in results:
        story.append(Paragraph("⚙️ Technology Stack", styles['SiconHeading']))
        story.append(HRFlowable(width="100%", thickness=1, color=SICON_GREEN, spaceAfter=10))
        tech = results['tech']
        
        technologies = tech.get('technologies', [])
        if technologies:
            tech_list = ", ".join([t.get('name', t) if isinstance(t, dict) else t for t in technologies])
            story.append(Paragraph(f"Detected Technologies: <b>{tech_list}</b>", styles['SiconBody']))
        else:
            story.append(Paragraph("No technologies detected.", styles['SiconBody']))
        story.append(Spacer(1, 20))
    
    # Directory Scan
    if 'dir' in results:
        story.append(Paragraph("📁 Directory Scan", styles['SiconHeading']))
        story.append(HRFlowable(width="100%", thickness=1, color=SICON_GREEN, spaceAfter=10))
        dir_data = results['dir']
        
        directories = dir_data.get('directories', [])
        if directories:
            story.append(Paragraph(f"Total Directories Found: <b>{len(directories)}</b>", styles['SiconBody']))
            
            dir_table_data = [["Status", "Path"]]
            for d in directories[:20]:  # Limit to 20
                dir_table_data.append([
                    str(d.get('status', '')),
                    d.get('path', '')[:60]
                ])
            
            dir_table = Table(dir_table_data, colWidths=[60, 400])
            dir_table.setStyle(TableStyle([
                ('BACKGROUND', (0, 0), (-1, 0), SICON_GREEN),
                ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
                ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
                ('FONTSIZE', (0, 0), (-1, -1), 9),
                ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
                ('BOTTOMPADDING', (0, 0), (-1, -1), 5),
                ('TOPPADDING', (0, 0), (-1, -1), 5),
            ]))
            story.append(dir_table)
        else:
            story.append(Paragraph("No directories found.", styles['SiconBody']))
        story.append(Spacer(1, 20))
    
    # Footer
    story.append(Spacer(1, 30))
    story.append(HRFlowable(width="100%", thickness=1, color=SICON_GRAY, spaceBefore=20, spaceAfter=10))
    story.append(Paragraph(
        f"<font size=8 color='gray'>Generated by S1C0N Security Reconnaissance Platform | {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</font>",
        ParagraphStyle('Footer', alignment=TA_CENTER)
    ))
    
    doc.build(story)
    buffer.seek(0)
    return buffer.getvalue()


def format_datetime(dt) -> str:
    """Format datetime for display."""
    if not dt:
        return "N/A"
    if isinstance(dt, str):
        try:
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        except:
            return dt
    return dt.strftime("%Y-%m-%d %H:%M:%S")


def get_table_style(is_positive: bool) -> TableStyle:
    """Get table style based on detection status."""
    return TableStyle([
        ('BACKGROUND', (0, 0), (0, -1), colors.Color(240/255, 240/255, 240/255)),
        ('FONTNAME', (0, 0), (0, -1), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.gray),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
    ])


def generate_summary(results: Dict[str, Any]) -> str:
    """Generate executive summary from scan results."""
    summary_parts = []
    
    # WAF Summary
    if 'waf' in results:
        waf = results['waf']
        if waf.get('detected'):
            summary_parts.append(f"The target is protected by <b>{waf.get('waf_name', 'a WAF')}</b>.")
        else:
            summary_parts.append("The target does <b>not have WAF protection</b> detected.")
    
    # Port Summary
    if 'port' in results:
        port = results['port']
        count = port.get('count', len(port.get('open_ports', [])))
        high_risk = len([p for p in port.get('open_ports', []) if p.get('risk') == 'high'])
        summary_parts.append(f"Found <b>{count} open ports</b>")
        if high_risk > 0:
            summary_parts[-1] += f" with <b>{high_risk} high-risk</b> services."
        else:
            summary_parts[-1] += "."
    
    # Subdomain Summary
    if 'subdo' in results:
        subdo = results['subdo']
        count = subdo.get('count', 0)
        summary_parts.append(f"Discovered <b>{count} subdomains</b> associated with the target.")
    
    # CMS Summary
    if 'cms' in results:
        cms = results['cms']
        if cms.get('detected'):
            version = f" version {cms.get('cms_version')}" if cms.get('cms_version') else ""
            summary_parts.append(f"Detected <b>{cms.get('cms_name')}{version}</b> as the content management system.")
    
    # Tech Summary
    if 'tech' in results:
        tech = results['tech']
        count = tech.get('count', len(tech.get('technologies', [])))
        if count > 0:
            summary_parts.append(f"Identified <b>{count} technologies</b> in the stack.")
    
    # Directory Summary
    if 'dir' in results:
        dir_data = results['dir']
        count = dir_data.get('count', len(dir_data.get('directories', [])))
        if count > 0:
            summary_parts.append(f"Found <b>{count} accessible directories</b>.")
    
    if not summary_parts:
        return "No scan results available."
    
    return " ".join(summary_parts)

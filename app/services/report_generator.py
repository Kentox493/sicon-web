"""
PDF Report Generator - Polished Neon Dark Theme
Features:
- Dedicated Cover Page
- AI Analysis & Findings
- Neon Design System
"""

import os
import io
from datetime import datetime
from typing import Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image, PageBreak
from reportlab.lib.enums import TA_CENTER, TA_LEFT, TA_RIGHT

from app.services.ai_summary import generate_ai_summary, generate_basic_summary
from app.services.chart_generator import create_findings_bar_chart

# Colors
BLACK = colors.Color(0, 0, 0)
GREEN = colors.Color(37/255, 211/255, 102/255)
DARK_GREEN = colors.Color(6/255, 30/255, 15/255)
WHITE = colors.Color(240/255, 255/255, 240/255)
GRAY = colors.Color(100/255, 100/255, 100/255)
RED = colors.Color(255/255, 82/255, 82/255)
ORANGE = colors.Color(255/255, 165/255, 0/255)
YELLOW = colors.Color(255/255, 235/255, 59/255)

BASE_DIR = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
LOGO_PATH = os.path.join(BASE_DIR, "web", "src", "assets", "logo.png")


def add_background(canvas, doc):
    """Background template for content pages."""
    canvas.saveState()
    canvas.setFillColor(BLACK)
    canvas.rect(0, 0, A4[0], A4[1], fill=1)
    
    # Simple border for content pages
    canvas.setStrokeColor(GREEN)
    canvas.setLineWidth(1)
    m = 10 * mm
    canvas.rect(m, m, A4[0] - 2*m, A4[1] - 2*m)
    
    # Page number
    page_num = canvas.getPageNumber()
    text = "Page %s" % page_num
    canvas.setFillColor(GRAY)
    canvas.setFont("Courier", 8)
    canvas.drawRightString(A4[0] - 15*mm, 15*mm, text)
    
    canvas.restoreState()


def add_cover_background(canvas, doc):
    """Background template specifically for the cover page."""
    canvas.saveState()
    canvas.setFillColor(BLACK)
    canvas.rect(0, 0, A4[0], A4[1], fill=1)
    
    # Neon corner accents
    canvas.setStrokeColor(GREEN)
    canvas.setLineWidth(3)
    margin = 15 * mm
    corner = 30 * mm
    
    # Top Left
    canvas.line(margin, A4[1]-margin, margin + corner, A4[1]-margin)
    canvas.line(margin, A4[1]-margin, margin, A4[1]-margin - corner)
    
    # Bottom Right
    canvas.line(A4[0]-margin, margin, A4[0]-margin - corner, margin)
    canvas.line(A4[0]-margin, margin, A4[0]-margin, margin + corner)
    
    canvas.restoreState()


def create_styles():
    styles = getSampleStyleSheet()
    # Updated text styles for better theme matching
    styles.add(ParagraphStyle('CoverTitle', fontName='Courier-Bold', fontSize=26, textColor=GREEN, alignment=TA_CENTER, spaceAfter=20, leading=32))
    styles.add(ParagraphStyle('CoverSubtitle', fontName='Courier', fontSize=14, textColor=WHITE, alignment=TA_CENTER, spaceAfter=40, spaceBefore=5))
    styles.add(ParagraphStyle('CoverLabel', fontName='Courier-Bold', fontSize=10, textColor=GREEN, alignment=TA_CENTER))
    styles.add(ParagraphStyle('CoverValue', fontName='Courier', fontSize=12, textColor=WHITE, alignment=TA_CENTER, spaceAfter=15))
    
    styles.add(ParagraphStyle('STitle', fontName='Helvetica-Bold', fontSize=18, textColor=WHITE, alignment=TA_CENTER, spaceAfter=5))
    styles.add(ParagraphStyle('SSubtitle', fontName='Helvetica', fontSize=11, textColor=GREEN, alignment=TA_CENTER, spaceAfter=15))
    styles.add(ParagraphStyle('SHeading', fontName='Helvetica-Bold', fontSize=12, textColor=GREEN, spaceBefore=15, spaceAfter=8))
    styles.add(ParagraphStyle('SBody', fontName='Courier', fontSize=9, textColor=WHITE, leading=12, spaceAfter=4))
    styles.add(ParagraphStyle('SSmall', fontName='Courier', fontSize=7, textColor=GRAY, alignment=TA_CENTER))
    styles.add(ParagraphStyle('SCell', fontName='Courier', fontSize=8, textColor=WHITE, leading=10, wordWrap='CJK'))
    return styles


def generate_scan_report(scan_data: Dict[str, Any], user_data: Dict[str, Any], 
                         use_ai: bool = False, api_key: str = None) -> bytes:
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, 
        rightMargin=15*mm, leftMargin=15*mm, topMargin=15*mm, bottomMargin=15*mm)
    
    styles = create_styles()
    story = []
    
    # --- COVER PAGE ---
    story.append(Spacer(1, 40*mm))
    
    # Large Logo
    try:
        if os.path.exists(LOGO_PATH):
            img = Image(LOGO_PATH, width=4*inch, height=2*inch, kind='proportional')
            img.hAlign = 'CENTER'
            story.append(img)
            story.append(Spacer(1, 15*mm))
    except:
        pass
        
    # Decorative terminal-style separator
    story.append(Paragraph("/// SYSTEM_REPORT_GENERATED ///", styles['SSmall']))
    story.append(Spacer(1, 10))
    
    story.append(Paragraph("SECURITY ASSESSMENT", styles['CoverTitle']))
    story.append(Paragraph("[ CONFIDENTIAL REPORT ]", styles['CoverSubtitle']))
    
    story.append(Spacer(1, 15*mm))
    
    # Scan Details Block
    target = scan_data.get('target', 'N/A').upper()
    scan_date = datetime.now().strftime("%B %d, %Y")
    analyst = user_data.get('username', 'Unknown').upper()
    scan_id = str(scan_data.get('id', 'N/A'))
    
    story.append(Paragraph("TARGET ASSET", styles['CoverLabel']))
    story.append(Paragraph(target, styles['CoverValue']))
    
    story.append(Paragraph("ASSESSMENT DATE", styles['CoverLabel']))
    story.append(Paragraph(scan_date, styles['CoverValue']))
    
    story.append(Paragraph("PREPARED FOR", styles['CoverLabel']))
    story.append(Paragraph(analyst, styles['CoverValue']))
    
    story.append(Paragraph("REFERENCE ID", styles['CoverLabel']))
    story.append(Paragraph(f"SCAN-{scan_id}", styles['CoverValue']))
    
    story.append(Spacer(1, 30*mm))
    story.append(HRFlowable(width="60%", thickness=1, color=GREEN))
    story.append(Spacer(1, 5*mm))
    story.append(Paragraph("CONFIDENTIAL DOCUMENT", styles['SSmall']))
    
    story.append(PageBreak())
    
    # --- REPORT CONTENT START ---
    
    # Info Header (Small)
    info_table = Table([
        [f"SCAN: #{scan_id}", f"TARGET: {target}", f"DATE: {datetime.now().strftime('%Y-%m-%d')}"]
    ], colWidths=[150, 200, 150])
    info_table.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (-1, -1), GRAY),
        ('FONTNAME', (0, 0), (-1, -1), 'Courier'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('LINEBELOW', (0, 0), (-1, -1), 0.5, GREEN),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(info_table)
    story.append(Spacer(1, 20))

    # Executive Summary
    ai_findings = []
    if use_ai and api_key:
        ai_result = generate_ai_summary(scan_data, api_key)
        summary_text = ai_result.get("summary", "")
        ai_findings = ai_result.get("findings", [])
        story.append(Paragraph("EXECUTIVE SUMMARY", styles['SHeading']))
    else:
        summary_text = generate_basic_summary(scan_data)
        story.append(Paragraph("SUMMARY", styles['SHeading']))
    
    summary_box = Table([[Paragraph(summary_text, styles['SBody'])]], colWidths=[480])
    summary_box.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, -1), DARK_GREEN),
        ('BOX', (0, 0), (-1, -1), 1, GREEN),
        ('LEFTPADDING', (0, 0), (-1, -1), 10),
        ('RIGHTPADDING', (0, 0), (-1, -1), 10),
        ('TOPPADDING', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 10),
    ]))
    story.append(summary_box)
    story.append(Spacer(1, 20))
    
    # Findings Table
    if use_ai and ai_findings:
        story.append(Paragraph("KEY FINDINGS & RECOMMENDATIONS", styles['SHeading']))
        
        data = [["FINDING", "SEV", "CVE", "ACTION"]]
        for f in ai_findings[:12]:
            finding = str(f.get('finding', ''))
            sev = str(f.get('severity', 'Info'))[:10]
            cve = str(f.get('cve', 'N/A'))
            action = str(f.get('action', f.get('recommendation', '')))
            data.append([
                Paragraph(finding, styles['SCell']),
                sev,
                Paragraph(cve, styles['SCell']),
                Paragraph(action, styles['SCell'])
            ])
        
        ft = Table(data, colWidths=[120, 45, 110, 205])
        style_list = [
            ('GRID', (0, 0), (-1, -1), 0.5, GREEN),
            ('BACKGROUND', (0, 0), (-1, 0), GREEN),
            ('TEXTCOLOR', (0, 0), (-1, 0), BLACK),
            ('FONTNAME', (0, 0), (-1, 0), 'Courier-Bold'),
            ('FONTSIZE', (0, 0), (-1, -1), 8),
            ('TEXTCOLOR', (0, 1), (-1, -1), WHITE),
            ('BACKGROUND', (0, 1), (-1, -1), BLACK),
            ('TOPPADDING', (0, 0), (-1, -1), 4),
            ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
            ('VALIGN', (0, 0), (-1, -1), 'TOP'),
        ]
        for i, f in enumerate(ai_findings[:12], 1):
            sev = str(f.get('severity', '')).lower()
            if 'critical' in sev:
                style_list.append(('TEXTCOLOR', (1, i), (1, i), RED))
            elif 'high' in sev:
                style_list.append(('TEXTCOLOR', (1, i), (1, i), ORANGE))
            elif 'medium' in sev:
                style_list.append(('TEXTCOLOR', (1, i), (1, i), YELLOW))
                
        ft.setStyle(TableStyle(style_list))
        story.append(ft)
        story.append(Spacer(1, 20))
        
    # Chart
    try:
        bar_buf = create_findings_bar_chart(scan_data)
        chart = Image(bar_buf, width=4*inch, height=1.6*inch)
        chart.hAlign = 'CENTER'
        story.append(Paragraph("SCAN STATISTICS", styles['SHeading']))
        story.append(chart)
        story.append(Spacer(1, 20))
    except:
        pass

    results = scan_data.get('results', {})
    
    # WAF
    if 'waf' in results:
        waf = results['waf']
        story.append(Paragraph("WAF PROTECTION", styles['SHeading']))
        wt = Table([
            ["Status", "PROTECTED" if waf.get('detected') else "EXPOSED"],
            ["Technology", waf.get('waf_name', 'N/A') or 'N/A'],
        ], colWidths=[100, 380])
        wt.setStyle(simple_table_style())
        story.append(wt)
        story.append(Spacer(1, 15))

    # Ports
    if 'port' in results:
        ports = results['port'].get('open_ports', [])
        if ports:
            story.append(Paragraph(f"OPEN PORTS ({len(ports)})", styles['SHeading']))
            for chunk_start in range(0, min(len(ports), 24), 12):
                chunk = ports[chunk_start:chunk_start+12]
                pd = [["Port", "Service", "Version", "Risk"]]
                for p in chunk:
                    pd.append([
                        f"{p.get('port')}/{p.get('protocol', 'tcp')}",
                        p.get('service', '?'),
                        (p.get('version', '') or '')[:25],
                        p.get('risk', 'low').upper()
                    ])
                pt = Table(pd, colWidths=[70, 100, 210, 100])
                pt.setStyle(simple_table_style(header=True))
                story.append(pt)
                story.append(Spacer(1, 5))
            story.append(Spacer(1, 15))

    # Subdomains
    if 'subdo' in results:
        subs = results['subdo'].get('subdomains', [])
        count = results['subdo'].get('count', 0)
        if subs:
            story.append(Paragraph(f"SUBDOMAINS ({count})", styles['SHeading']))
            max_subs = min(len(subs), 60)
            for chunk_start in range(0, max_subs, 20):
                chunk = subs[chunk_start:chunk_start+20]
                sd = [["#", "Subdomain"]]
                for i, s in enumerate(chunk, chunk_start + 1):
                    name = s.get('subdomain', s) if isinstance(s, dict) else s
                    sd.append([str(i), name[:50]])
                st = Table(sd, colWidths=[40, 440])
                st.setStyle(simple_table_style(header=(chunk_start == 0)))
                story.append(st)
                story.append(Spacer(1, 5))
            if len(subs) > 60:
                story.append(Paragraph(f"... {len(subs)-60} more hidden", styles['SSmall']))
            story.append(Spacer(1, 15))

    # Tech
    if 'tech' in results or 'cms' in results:
        story.append(Paragraph("TECHNOLOGIES", styles['SHeading']))
        td = [["Type", "Name"]]
        if results.get('cms', {}).get('detected'):
            cms = results['cms']
            td.append(["CMS", f"{cms.get('cms_name', '')} {cms.get('cms_version', '')}"])
        for t in results.get('tech', {}).get('technologies', [])[:10]:
            name = t.get('name', t) if isinstance(t, dict) else t
            td.append(["Stack", str(name)[:50]])
        if len(td) > 1:
            tt = Table(td, colWidths=[80, 400])
            tt.setStyle(simple_table_style(header=True))
            story.append(tt)
        story.append(Spacer(1, 15))

    # Directories
    if 'dir' in results:
        dirs = results['dir'].get('directories', [])
        if dirs:
            story.append(Paragraph(f"DIRECTORIES ({len(dirs)})", styles['SHeading']))
            
            # Limit and chunk
            max_dirs = min(len(dirs), 30)
            for chunk_start in range(0, max_dirs, 15):
                chunk = dirs[chunk_start:chunk_start+15]
                dd = [["Status", "Path", "Severity"]]
                for d in chunk:
                    dd.append([
                        str(d.get('status', '?')),
                        str(d.get('path', ''))[:45],
                        str(d.get('severity', 'info')).upper()
                    ])
                dt = Table(dd, colWidths=[60, 330, 90])
                dt.setStyle(simple_table_style(header=(chunk_start == 0)))
                story.append(dt)
                if chunk_start + 15 < max_dirs:
                    story.append(Spacer(1, 4))
            
            if len(dirs) > 30:
                story.append(Paragraph(f"... and {len(dirs) - 30} more directories", styles['SSmall']))
            story.append(Spacer(1, 15))

    # WordPress Enumeration
    if 'wp' in results:
        wp = results['wp']
        if wp.get('wordpress_detected'):
            story.append(Paragraph("WORDPRESS ENUMERATION", styles['SHeading']))
            
            # WP Info table
            wp_info = [
                ["Property", "Value"],
                ["WordPress Detected", "Yes"],
                ["Version", wp.get('version', 'Unknown') or 'Unknown'],
            ]
            wpt = Table(wp_info, colWidths=[120, 360])
            wpt.setStyle(simple_table_style(header=True))
            story.append(wpt)
            story.append(Spacer(1, 10))
            
            # Plugins
            plugins = wp.get('plugins', [])
            if plugins:
                story.append(Paragraph(f"Plugins ({len(plugins)})", styles['SBody']))
                pd = [["Plugin", "Version", "Outdated", "Vulns"]]
                for p in plugins[:15]:
                    pd.append([
                        str(p.get('name', ''))[:30],
                        str(p.get('version', '?'))[:15],
                        "Yes" if p.get('outdated') else "No",
                        str(p.get('vulnerabilities', 0))
                    ])
                pt = Table(pd, colWidths=[180, 100, 80, 60])
                pt.setStyle(simple_table_style(header=True))
                story.append(pt)
                story.append(Spacer(1, 8))
            
            # Themes
            themes = wp.get('themes', [])
            if themes:
                story.append(Paragraph(f"Themes ({len(themes)})", styles['SBody']))
                td = [["Theme", "Version", "Outdated"]]
                for t in themes[:10]:
                    td.append([
                        str(t.get('name', ''))[:40],
                        str(t.get('version', '?'))[:15],
                        "Yes" if t.get('outdated') else "No"
                    ])
                tt = Table(td, colWidths=[250, 100, 80])
                tt.setStyle(simple_table_style(header=True))
                story.append(tt)
                story.append(Spacer(1, 8))
            
            # Users
            users = wp.get('users', [])
            if users:
                story.append(Paragraph(f"Enumerated Users ({len(users)})", styles['SBody']))
                ud = [["ID", "Username"]]
                for u in users[:20]:
                    ud.append([str(u.get('id', '?')), str(u.get('username', ''))[:40]])
                ut = Table(ud, colWidths=[60, 420])
                ut.setStyle(simple_table_style(header=True))
                story.append(ut)
                story.append(Spacer(1, 8))
            
            # Vulnerabilities
            vulns = wp.get('vulnerabilities', [])
            if vulns:
                story.append(Paragraph(f"Known Vulnerabilities ({len(vulns)})", styles['SBody']))
                vd = [["Component", "Title", "Severity"]]
                for v in vulns[:10]:
                    vd.append([
                        str(v.get('component', ''))[:25],
                        str(v.get('title', ''))[:35],
                        str(v.get('severity', 'medium')).upper()
                    ])
                vt = Table(vd, colWidths=[120, 280, 80])
                vt.setStyle(simple_table_style(header=True))
                story.append(vt)
            
            story.append(Spacer(1, 15))

    # Footer
    story.append(Spacer(1, 20))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GREEN))
    story.append(Paragraph(f"GENERATED BY S1C0N PLATFORM", styles['SSmall']))

    # Build with dual template (Cover vs Content)
    doc.build(story, onFirstPage=add_cover_background, onLaterPages=add_background)
    buffer.seek(0)
    return buffer.getvalue()


def simple_table_style(header=False):
    style = [
        ('GRID', (0, 0), (-1, -1), 0.5, GREEN),
        ('FONTNAME', (0, 0), (-1, -1), 'Courier'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 0), (-1, -1), WHITE),
        ('BACKGROUND', (0, 0), (-1, -1), BLACK),
        ('TOPPADDING', (0, 0), (-1, -1), 4),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 4),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]
    if header:
        style.extend([
            ('BACKGROUND', (0, 0), (-1, 0), GREEN),
            ('TEXTCOLOR', (0, 0), (-1, 0), BLACK),
            ('FONTNAME', (0, 0), (-1, 0), 'Courier-Bold'),
        ])
    return TableStyle(style)

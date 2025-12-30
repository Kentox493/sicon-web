"""
PDF Report Generator - Polished Neon Dark Theme
Clean layout with proper text wrapping and page management.
"""

import os
import io
from datetime import datetime
from typing import Dict, Any
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch, mm
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, HRFlowable, Image
from reportlab.lib.enums import TA_CENTER, TA_LEFT

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
    canvas.saveState()
    canvas.setFillColor(BLACK)
    canvas.rect(0, 0, A4[0], A4[1], fill=1)
    canvas.setStrokeColor(GREEN)
    canvas.setLineWidth(1)
    m = 8 * mm
    canvas.rect(m, m, A4[0] - 2*m, A4[1] - 2*m)
    canvas.restoreState()


def create_styles():
    styles = getSampleStyleSheet()
    styles.add(ParagraphStyle('STitle', fontName='Helvetica-Bold', fontSize=20, textColor=WHITE, alignment=TA_CENTER, spaceAfter=5))
    styles.add(ParagraphStyle('SSubtitle', fontName='Helvetica', fontSize=11, textColor=GREEN, alignment=TA_CENTER, spaceAfter=15))
    styles.add(ParagraphStyle('SHeading', fontName='Helvetica-Bold', fontSize=12, textColor=GREEN, spaceBefore=10, spaceAfter=6))
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
    
    # Header
    try:
        if os.path.exists(LOGO_PATH):
            img = Image(LOGO_PATH, width=2*inch, height=1*inch, kind='proportional')
            img.hAlign = 'CENTER'
            story.append(img)
    except:
        story.append(Paragraph("S1C0N", styles['STitle']))
    
    story.append(Spacer(1, 5))
    story.append(Paragraph("SECURITY RECONNAISSANCE REPORT", styles['SSubtitle']))
    
    # Info Box
    info = [
        ["Target:", scan_data.get('target', 'N/A')],
        ["Scan ID:", f"#{scan_data.get('id', 'N/A')}"],
        ["Date:", datetime.now().strftime("%Y-%m-%d %H:%M")],
        ["Analyst:", user_data.get('username', 'Unknown')],
    ]
    t = Table(info, colWidths=[60, 400])
    t.setStyle(TableStyle([
        ('TEXTCOLOR', (0, 0), (0, -1), GREEN),
        ('TEXTCOLOR', (1, 0), (1, -1), WHITE),
        ('FONTNAME', (0, 0), (-1, -1), 'Courier-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('LINEBELOW', (0, -1), (-1, -1), 0.5, GREEN),
    ]))
    story.append(t)
    story.append(Spacer(1, 25))
    
    # Summary
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
        ('LEFTPADDING', (0, 0), (-1, -1), 8),
        ('RIGHTPADDING', (0, 0), (-1, -1), 8),
        ('TOPPADDING', (0, 0), (-1, -1), 8),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 8),
    ]))
    story.append(summary_box)
    story.append(Spacer(1, 25))
    
    # AI Findings Table (with proper text wrapping)
    if use_ai and ai_findings:
        story.append(Paragraph("KEY FINDINGS & CVE REFERENCES", styles['SHeading']))
        
        data = [["FINDING", "SEV", "CVE", "ACTION"]]
        for f in ai_findings[:10]:
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
        
        # Adjusted column widths for better wrapping
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
        for i, f in enumerate(ai_findings[:10], 1):
            sev = str(f.get('severity', '')).lower()
            if 'critical' in sev:
                style_list.append(('TEXTCOLOR', (1, i), (1, i), RED))
            elif 'high' in sev:
                style_list.append(('TEXTCOLOR', (1, i), (1, i), ORANGE))
            elif 'medium' in sev:
                style_list.append(('TEXTCOLOR', (1, i), (1, i), YELLOW))
        
        ft.setStyle(TableStyle(style_list))
        story.append(ft)
        story.append(Spacer(1, 25))
    
    # Chart
    try:
        bar_buf = create_findings_bar_chart(scan_data)
        chart = Image(bar_buf, width=4*inch, height=1.6*inch)
        chart.hAlign = 'CENTER'
        story.append(Paragraph("STATISTICS", styles['SHeading']))
        story.append(chart)
        story.append(Spacer(1, 20))
    except:
        pass

    results = scan_data.get('results', {})
    
    # WAF
    if 'waf' in results:
        waf = results['waf']
        story.append(Paragraph("WAF STATUS", styles['SHeading']))
        wt = Table([
            ["Status", "PROTECTED" if waf.get('detected') else "EXPOSED"],
            ["Name", waf.get('waf_name', 'N/A') or 'N/A'],
        ], colWidths=[80, 400])
        wt.setStyle(simple_table_style())
        story.append(wt)
        story.append(Spacer(1, 20))

    # Ports - Split into chunks if too many
    if 'port' in results:
        ports = results['port'].get('open_ports', [])
        if ports:
            story.append(Paragraph(f"OPEN PORTS ({len(ports)})", styles['SHeading']))
            
            # Limit to 12 per table to avoid page overflow
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
                if chunk_start + 12 < min(len(ports), 24):
                    story.append(Spacer(1, 4))
            story.append(Spacer(1, 20))

    # Subdomains - Split into chunks
    if 'subdo' in results:
        subs = results['subdo'].get('subdomains', [])
        count = results['subdo'].get('count', 0)
        if subs:
            story.append(Paragraph(f"SUBDOMAINS ({count})", styles['SHeading']))
            
            # Split into chunks of 20
            max_subs = min(len(subs), 60)
            for chunk_start in range(0, max_subs, 20):
                chunk = subs[chunk_start:chunk_start+20]
                sd = [["#", "Subdomain"]]
                for i, s in enumerate(chunk, chunk_start + 1):
                    name = s.get('subdomain', s) if isinstance(s, dict) else s
                    sd.append([str(i), name[:50]])
                st = Table(sd, colWidths=[35, 445])
                st.setStyle(simple_table_style(header=(chunk_start == 0)))
                story.append(st)
                if chunk_start + 20 < max_subs:
                    story.append(Spacer(1, 4))
            
            if len(subs) > 60:
                story.append(Paragraph(f"... and {len(subs) - 60} more subdomains", styles['SSmall']))
            story.append(Spacer(1, 20))

    # Tech
    if 'tech' in results or 'cms' in results:
        story.append(Paragraph("TECHNOLOGIES", styles['SHeading']))
        td = [["Type", "Name"]]
        if results.get('cms', {}).get('detected'):
            cms = results['cms']
            td.append(["CMS", f"{cms.get('cms_name', '')} {cms.get('cms_version', '')}"])
        for t in results.get('tech', {}).get('technologies', [])[:8]:
            name = t.get('name', t) if isinstance(t, dict) else t
            td.append(["Tech", str(name)[:50]])
        if len(td) > 1:
            tt = Table(td, colWidths=[70, 410])
            tt.setStyle(simple_table_style(header=True))
            story.append(tt)
        story.append(Spacer(1, 20))

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
            story.append(Spacer(1, 20))

    # Footer
    story.append(Spacer(1, 30))
    story.append(HRFlowable(width="100%", thickness=0.5, color=GREEN))
    story.append(Paragraph(f"S1C0N | {datetime.now().strftime('%Y')}", styles['SSmall']))

    doc.build(story, onFirstPage=add_background, onLaterPages=add_background)
    buffer.seek(0)
    return buffer.getvalue()


def simple_table_style(header=False):
    style = [
        ('GRID', (0, 0), (-1, -1), 0.5, GREEN),
        ('FONTNAME', (0, 0), (-1, -1), 'Courier'),
        ('FONTSIZE', (0, 0), (-1, -1), 8),
        ('TEXTCOLOR', (0, 0), (-1, -1), WHITE),
        ('BACKGROUND', (0, 0), (-1, -1), BLACK),
        ('TOPPADDING', (0, 0), (-1, -1), 3),
        ('BOTTOMPADDING', (0, 0), (-1, -1), 3),
        ('VALIGN', (0, 0), (-1, -1), 'TOP'),
    ]
    if header:
        style.extend([
            ('BACKGROUND', (0, 0), (-1, 0), GREEN),
            ('TEXTCOLOR', (0, 0), (-1, 0), BLACK),
            ('FONTNAME', (0, 0), (-1, 0), 'Courier-Bold'),
        ])
    return TableStyle(style)

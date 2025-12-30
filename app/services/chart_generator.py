"""
Chart Generator Service
Generates Neon-style charts for PDF reports using Matplotlib.
"""
import matplotlib.pyplot as plt
import io
import numpy as np

# Neon palette
NEON_GREEN = '#25D366'
NEON_BLACK = '#000000'
NEON_DARK_GREEN = '#061E0F'
NEON_GRAY = '#646464'
NEON_WHITE = '#F0FFF0'

def create_severity_pie_chart(scan_data: dict) -> io.BytesIO:
    """Creates a donut chart of finding severities."""
    results = scan_data.get('results', {})
    
    # Calculate stats
    high = 0
    medium = 0
    low = 0
    info = 0
    
    # WAF
    if not results.get('waf', {}).get('detected'):
        high += 1 # Unprotected WAF is high risk
    else:
        info += 1
        
    # Ports
    for p in results.get('port', {}).get('open_ports', []):
        risk = p.get('risk', 'low')
        if risk == 'high': high += 1
        elif risk == 'medium': medium += 1
        else: low += 1
        
    # CMS (Vulnerability assumption or info)
    if results.get('cms', {}).get('detected'):
        info += 1
        
    data = [high, medium, low, info]
    labels = ['High', 'Medium', 'Low', 'Info']
    colors = ['#FF3333', '#FFA500', '#FFFF00', NEON_GREEN] # Red, Orange, Yellow, Green
    
    # Filter zeros
    plot_data = []
    plot_labels = []
    plot_colors = []
    for d, l, c in zip(data, labels, colors):
        if d > 0:
            plot_data.append(d)
            plot_labels.append(l)
            plot_colors.append(c)
            
    if not plot_data:
        plot_data = [1]
        plot_labels = ['No Significant Findings']
        plot_colors = [NEON_GREEN]

    # Setup dark style
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(6, 4))
    fig.patch.set_facecolor(NEON_BLACK)
    ax.set_facecolor(NEON_BLACK)
    
    # Pie chart
    wedges, texts, autotexts = ax.pie(plot_data, labels=plot_labels, autopct='%1.1f%%',
                                    startangle=90, colors=plot_colors,
                                    textprops={'color': NEON_WHITE, 'fontsize': 10},
                                    wedgeprops={'width': 0.4, 'edgecolor': NEON_BLACK})
                                    
    # Center text
    total = sum(data)
    ax.text(0, 0, f"{total}\nFindings", ha='center', va='center', fontsize=12, fontweight='bold', color=NEON_WHITE)
    
    # Save
    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor=NEON_BLACK, transparent=True, dpi=300, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf

def create_findings_bar_chart(scan_data: dict) -> io.BytesIO:
    """Creates a bar chart of findings by category."""
    results = scan_data.get('results', {})
    
    categories = ['Ports', 'Subdomains', 'Dirs', 'Tech']
    counts = [
        len(results.get('port', {}).get('open_ports', [])),
        results.get('subdo', {}).get('count', 0),
        len(results.get('dir', {}).get('directories', [])),
        len(results.get('tech', {}).get('technologies', []))
    ]
    
    # Setup dark style
    plt.style.use('dark_background')
    fig, ax = plt.subplots(figsize=(6, 3))
    fig.patch.set_facecolor(NEON_BLACK)
    ax.set_facecolor(NEON_BLACK)
    
    # Bar chart
    bars = ax.bar(categories, counts, color=NEON_GREEN, alpha=0.8, width=0.5)
    
    # Styling
    ax.spines['top'].set_visible(False)
    ax.spines['right'].set_visible(False)
    ax.spines['left'].set_color(NEON_GREEN)
    ax.spines['bottom'].set_color(NEON_GREEN)
    
    ax.tick_params(axis='x', colors=NEON_WHITE)
    ax.tick_params(axis='y', colors=NEON_WHITE)
    
    # Add values on top
    for bar in bars:
        height = bar.get_height()
        ax.text(bar.get_x() + bar.get_width()/2., height,
                '%d' % int(height),
                ha='center', va='bottom', color=NEON_WHITE)
                
    # Save
    buf = io.BytesIO()
    plt.savefig(buf, format='png', facecolor=NEON_BLACK, transparent=True, dpi=300, bbox_inches='tight')
    plt.close()
    buf.seek(0)
    return buf

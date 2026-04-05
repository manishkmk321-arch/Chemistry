from flask import Blueprint, render_template, request, session, redirect, url_for, send_file
import json
import io
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors
from calculations.pdf_utils import get_standard_styles, add_pdf_header, get_standard_table_style

exp6_bp = Blueprint('exp6', __name__)

def linear_regression(x, y):
    n = len(x)
    if n < 2:
        return 0, 0
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    sum_x2 = sum(xi * xi for xi in x)
    
    denom = n * sum_x2 - sum_x * sum_x
    if denom == 0:
        return 0, 0
    
    m = (n * sum_xy - sum_x * sum_y) / denom
    c = (sum_y - m * sum_x) / n
    
    return m, c

def find_intersections(volumes, conductance):
    n = len(volumes)
    
    min_idx = conductance.index(min(conductance))
    
    if min_idx < 2 or min_idx > n - 3:
        return volumes[min_idx], volumes[min_idx]
    
    v1_data = volumes[:min_idx + 1]
    c1_data = conductance[:min_idx + 1]
    
    v3_data = volumes[min_idx:]
    c3_data = conductance[min_idx:]
    
    mid_start = max(0, min_idx - 2)
    mid_end = min(n - 1, min_idx + 2)
    v2_data = volumes[mid_start:mid_end + 1]
    c2_data = conductance[mid_start:mid_end + 1]
    
    m1, c1 = linear_regression(v1_data, c1_data)
    m2, c2 = linear_regression(v2_data, c2_data)
    m3, c3 = linear_regression(v3_data, c3_data)
    
    if m1 != m2:
        v1 = (c2 - c1) / (m1 - m2)
    else:
        v1 = v1_data[-1]
    
    if m2 != m3:
        v2 = (c3 - c2) / (m2 - m3)
    else:
        v2 = v3_data[0]
    
    return v1, v2

@exp6_bp.route('/')
def index():
    return render_template('exp6/mixture_conductometry.html')

@exp6_bp.route('/calculate', methods=['POST'])
def calculate():
    volumes = [float(v) for v in request.form.getlist('volumes')]
    conductance = [float(c) for c in request.form.getlist('conductance')]
    
    if len(volumes) < 5 or len(conductance) < 5:
        return render_template('exp6/mixture_conductometry.html', error="Please enter at least 5 readings")
    
    v1, v2 = find_intersections(volumes, conductance)
    
    min_idx = conductance.index(min(conductance))
    
    v1_line = volumes[:min_idx + 1]
    c1_line = conductance[:min_idx + 1]
    v3_line = volumes[min_idx:]
    c3_line = conductance[min_idx:]
    mid_start = max(0, min_idx - 2)
    mid_end = min(len(volumes) - 1, min_idx + 2)
    v2_line = volumes[mid_start:mid_end + 1]
    c2_line = conductance[mid_start:mid_end + 1]
    
    m1, c1_intercept = linear_regression(v1_line, c1_line)
    m2, c2_intercept = linear_regression(v2_line, c2_line)
    m3, c3_intercept = linear_regression(v3_line, c3_line)
    
    line1_y = [m1 * v + c1_intercept for v in volumes]
    line2_y = [m2 * v + c2_intercept for v in volumes]
    line3_y = [m3 * v + c3_intercept for v in volumes]
    
    graph_data = {
        'labels': volumes,
        'conductance': conductance,
        'line1': line1_y,
        'line2': line2_y,
        'line3': line3_y,
        'v1': round(v1, 2),
        'v2': round(v2, 2)
    }
    
    session['volumes'] = volumes
    session['conductance'] = conductance
    session['v1'] = v1
    session['v2'] = v2
    session['graph_data'] = json.dumps(graph_data)
    
    return render_template('exp6/mixture_conductometry_intermediate.html',
                         v1=round(v1, 2),
                         v2=round(v2, 2),
                         v3=round(v2 - v1, 2),
                         graph_data=json.dumps(graph_data))

@exp6_bp.route('/final_result', methods=['POST'])
def final_result():
    volumes = session.get('volumes')
    conductance = session.get('conductance')
    graph_data = session.get('graph_data')
    
    v1 = session.get('v1')
    v2 = session.get('v2')
    
    N1 = float(request.form.get('norm_naoh'))
    V2 = float(request.form.get('vol_hcl'))
    V4 = float(request.form.get('vol_ch3cooh'))
    
    v3 = v2 - v1
    
    N2 = (N1 * v1) / V2
    Amount_HCl = (N2 * 36.5) / 10
    
    N3 = N1
    N4 = (N3 * v3) / V4
    Amount_CH3COOH = (N4 * 60) / 10
    
    return render_template('exp6/mixture_conductometry_result.html',
                         volumes=volumes,
                         conductance=conductance,
                         v1=round(v1, 2),
                         v2=round(v2, 2),
                         v3=round(v3, 2),
                         N1=N1,
                         V2=V2,
                         V4=V4,
                         N2=round(N2, 4),
                         N4=round(N4, 4),
                         Amount_HCl=round(Amount_HCl, 4),
                         Amount_CH3COOH=round(Amount_CH3COOH, 4),
                         graph_data=graph_data)

@exp6_bp.route('/download_pdf', methods=['POST'])
def download_pdf():
    from calculations.pdf_utils import get_standard_styles, add_pdf_header, get_standard_table_style
    
    result_data_raw = request.form.get('result_data')
    try:
        result_data = json.loads(result_data_raw) if result_data_raw and result_data_raw.strip() else {}
    except Exception:
        result_data = {}
    
    table_data_raw = request.form.get('table_data')
    try:
        table_data = json.loads(table_data_raw) if table_data_raw and table_data_raw.strip() else []
    except Exception:
        table_data = []
    
    include_graph = request.form.get('include_graph', 'false') == 'true'
    student_name = request.form.get('student_name', '')
    reg_number = request.form.get('reg_number', '')
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    
    styles, title_style, h2_style, normal_style, calc_style, header_style, subheader_style = get_standard_styles()
    
    elements = []
    
    add_pdf_header(elements, 'exp6', datetime.now().strftime('%d-%m-%Y'), student_name, reg_number, title_style, normal_style, header_style, subheader_style)
    
    elements.append(Paragraph("OBSERVATION TABLE", h2_style))
    
    if table_data:
        table_list = [['S.N.', 'Volume of NaOH\nAdded (mL)', 'Conductance\n(ohm⁻¹)']]
        for i, row in enumerate(table_data, 1):
            table_list.append([str(i), str(row.get('volume', '')), str(row.get('conductance', ''))])
        
        col_widths = [50, 200, 200]
        t = Table(table_list, colWidths=col_widths)
        t.setStyle(get_standard_table_style())
        elements.append(t)
        elements.append(Spacer(1, 15))
    
    if include_graph:
        volumes = result_data.get('volumes', [])
        conductance_vals = result_data.get('conductance', [])
        line1_y = result_data.get('line1', [])
        line2_y = result_data.get('line2', [])
        line3_y = result_data.get('line3', [])
        v1_val = result_data.get('v1', 0)
        v2_val = result_data.get('v2', 0)
        
        if volumes and conductance_vals:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            
            fig, ax = plt.subplots(figsize=(7, 4.5))
            ax.plot(volumes, conductance_vals, 'g-o', markersize=5, label='Conductance')
            if line1_y:
                ax.plot(volumes, line1_y, 'b--', linewidth=1.5, label='Line 1')
            if line2_y:
                ax.plot(volumes, line2_y, 'r--', linewidth=1.5, label='Line 2')
            if line3_y:
                ax.plot(volumes, line3_y, 'm--', linewidth=1.5, label='Line 3')
            ax.axvline(x=v1_val, color='purple', linestyle=':', linewidth=1.5, label=f'V1 ({v1_val:.2f} mL)')
            ax.axvline(x=v2_val, color='orange', linestyle=':', linewidth=1.5, label=f'V2 ({v2_val:.2f} mL)')
            ax.set_xlabel('Volume of NaOH (mL)', fontsize=11)
            ax.set_ylabel('Conductance (ohm⁻¹)', fontsize=11)
            ax.set_title('Conductance vs Volume of NaOH (Mixture)', fontsize=12, fontweight='bold')
            ax.legend(fontsize=9)
            ax.grid(True, alpha=0.3)
            
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close(fig)
            
            elements.append(Image(img_buffer, width=400, height=240))
            elements.append(Spacer(1, 15))
    
    elements.append(Paragraph("CALCULATION", h2_style))
    
    v1 = result_data.get('v1', 0)
    v2 = result_data.get('v2', 0)
    v3 = v2 - v1
    N1 = result_data.get('N1', 0)
    V2 = result_data.get('V2', 0)
    V4 = result_data.get('V4', 0)
    N2 = result_data.get('N2', 0)
    N4 = result_data.get('N4', 0)
    amount_hcl = result_data.get('Amount_HCl', 0)
    amount_ch3cooh = result_data.get('Amount_CH3COOH', 0)
    
    elements.append(Paragraph("For HCl:", normal_style))
    elements.append(Paragraph(f"N₂ = (N₁ × V₁) / V₂ = ({N1:.4f} × {v1:.2f}) / {V2:.2f} = {N2:.4f} N", calc_style))
    elements.append(Paragraph(f"Amount of HCl = (N₂ × 36.5) / 10 = ({N2:.4f} × 36.5) / 10 = {amount_hcl:.4f} g", calc_style))
    elements.append(Spacer(1, 10))
    
    elements.append(Paragraph("For CH₃COOH:", normal_style))
    elements.append(Paragraph(f"V₃ = V₂ − V₁ = {v2:.2f} − {v1:.2f} = {v3:.2f} mL", calc_style))
    elements.append(Paragraph(f"N₄ = (N₁ × V₃) / V₄ = ({N1:.4f} × {v3:.2f}) / {V4:.2f} = {N4:.4f} N", calc_style))
    elements.append(Paragraph(f"Amount of CH₃COOH = (N₄ × 60) / 10 = ({N4:.4f} × 60) / 10 = {amount_ch3cooh:.4f} g", calc_style))
    elements.append(Spacer(1, 15))
    
    elements.append(Paragraph("FINAL RESULT", h2_style))
    result_table = Table([
        ['I End Point Volume (V1)', f'{v1:.2f} mL'],
        ['II End Point Volume (V2)', f'{v2:.2f} mL'],
        ['Volume of NaOH for CH₃COOH (V3)', f'{v3:.2f} mL'],
        ['Strength of HCl (N₂)', f'{N2:.4f} N'],
        ['Strength of CH₃COOH (N₄)', f'{N4:.4f} N'],
        ['Amount of HCl', f'{amount_hcl:.4f} g'],
        ['Amount of CH₃COOH', f'{amount_ch3cooh:.4f} g']
    ], colWidths=[250, 150])
    result_table.setStyle(get_standard_table_style())
    elements.append(result_table)
    
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name=f"Exp6_{reg_number}.pdf", mimetype='application/pdf')

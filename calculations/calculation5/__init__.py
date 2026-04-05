from flask import Blueprint, render_template, request, send_file
import io
import json
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt

exp5_bp = Blueprint('exp5', __name__)

def find_intersection(volumes, conductance):
    n = len(volumes)
    
    min_conductance = min(conductance)
    min_idx = conductance.index(min_conductance)
    
    v1 = volumes[:min_idx + 1]
    c1 = conductance[:min_idx + 1]
    
    v2 = volumes[min_idx:]
    c2 = conductance[min_idx:]
    
    if len(v1) < 2 or len(v2) < 2:
        return volumes[min_idx]
    
    m1, c1_intercept = linear_regression(v1, c1)
    m2, c2_intercept = linear_regression(v2, c2)
    
    if m1 == m2:
        return volumes[min_idx]
    
    ve = (c2_intercept - c1_intercept) / (m1 - m2)
    
    return ve

def linear_regression(x, y):
    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    sum_x2 = sum(xi * xi for xi in x)
    
    m = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
    c = (sum_y - m * sum_x) / n
    
    return m, c

@exp5_bp.route('/')
def index():
    return render_template('exp5/conductometry.html')

@exp5_bp.route('/calculate', methods=['POST'])
def calculate():
    volumes = [float(v) for v in request.form.getlist('volumes')]
    conductance = [float(c) for c in request.form.getlist('conductance')]
    norm_naoh = float(request.form.get('norm_naoh'))
    vol_acid = float(request.form.get('vol_acid'))
    
    if len(volumes) < 3 or len(conductance) < 3:
        return render_template('exp5/conductometry.html', error="Please enter at least 3 readings")
    
    ve = find_intersection(volumes, conductance)
    
    norm_hcl = (norm_naoh * ve) / vol_acid
    amount_hcl = (norm_hcl * 36.5) / 10
    
    min_idx = conductance.index(min(conductance))
    
    v1 = volumes[:min_idx + 1]
    c1 = conductance[:min_idx + 1]
    v2 = volumes[min_idx:]
    c2 = conductance[min_idx:]
    
    m1, c1_intercept = linear_regression(v1, c1)
    m2, c2_intercept = linear_regression(v2, c2)
    
    line1_y = [m1 * v + c1_intercept for v in volumes]
    line2_y = [m2 * v + c2_intercept for v in volumes]
    
    graph_data = {
        'labels': volumes,
        'conductance': conductance,
        'line1': line1_y,
        'line2': line2_y
    }
    
    return render_template('exp5/conductometry_result.html',
                         volumes=volumes,
                         conductance=conductance,
                         ve=round(ve, 2),
                         norm_naoh=norm_naoh,
                         vol_acid=vol_acid,
                         norm_hcl=round(norm_hcl, 4),
                         amount_hcl=round(amount_hcl, 4),
                         graph_data=json.dumps(graph_data))

@exp5_bp.route('/download_pdf', methods=['POST'])
def download_pdf():
    from calculations.pdf_utils import get_standard_styles, add_pdf_header, get_standard_table_style

    # Safe JSON parsing
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

    add_pdf_header(elements, 'exp5', datetime.now().strftime('%d-%m-%Y'), student_name, reg_number, title_style, normal_style, header_style, subheader_style)

    # Observation Table
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

    # Graph
    if include_graph:
        volumes = result_data.get('volumes', [])
        conductance_vals = result_data.get('conductance', [])
        line1_y = result_data.get('line1_y', [])
        line2_y = result_data.get('line2_y', [])
        ve = result_data.get('ve', 0)

        if volumes and conductance_vals:
            fig, ax = plt.subplots(figsize=(7, 4.5))
            ax.plot(volumes, conductance_vals, 'g-o', markersize=5, label='Conductance')
            if line1_y:
                ax.plot(volumes, line1_y, 'b--', linewidth=1.5, label='Line 1')
            if line2_y:
                ax.plot(volumes, line2_y, 'r--', linewidth=1.5, label='Line 2')
            ax.axvline(x=ve, color='purple', linestyle=':', linewidth=1.5, label=f'Equivalence Point ({ve:.2f} mL)')
            ax.set_xlabel('Volume of NaOH (mL)', fontsize=11)
            ax.set_ylabel('Conductance (ohm⁻¹)', fontsize=11)
            ax.set_title('Conductance vs Volume of NaOH', fontsize=12, fontweight='bold')
            ax.legend(fontsize=9)
            ax.grid(True, alpha=0.3)

            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close(fig)

            elements.append(Image(img_buffer, width=400, height=240))
            elements.append(Spacer(1, 15))

    # Calculation
    ve = result_data.get('ve', 0)
    norm_naoh = result_data.get('normNaoh', 0)
    vol_acid = result_data.get('volAcid', 0)
    norm_hcl = result_data.get('normHcl', 0)
    amount_hcl = result_data.get('amountHcl', 0)

    elements.append(Paragraph("CALCULATIONS", h2_style))
    elements.append(Paragraph("Using formula: N₁ × V₁ = N₂ × V₂", normal_style))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph("Where:", normal_style))
    elements.append(Paragraph(f"V₁ = Volume of NaOH from graph = {ve:.2f} mL", calc_style))
    elements.append(Paragraph(f"N₁ = Normality of NaOH = {norm_naoh} N", calc_style))
    elements.append(Paragraph(f"V₂ = Volume of HCl taken = {vol_acid} mL", calc_style))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph(f"N₂ (HCl) = (N₁ × V₁) / V₂ = ({norm_naoh} × {ve:.2f}) / {vol_acid}", normal_style))
    elements.append(Paragraph(f"         = {norm_hcl:.4f} N", calc_style))
    elements.append(Spacer(1, 5))
    elements.append(Paragraph(f"Amount of HCl = (N₂ × 36.5) / 10", normal_style))
    elements.append(Paragraph(f"              = ({norm_hcl:.4f} × 36.5) / 10", calc_style))
    elements.append(Paragraph(f"              = {amount_hcl:.4f} g/L", calc_style))
    elements.append(Spacer(1, 15))

    # Final Result
    elements.append(Paragraph("FINAL RESULT", h2_style))
    result_table = [
        ['Parameter', 'Value'],
        ['Volume of NaOH from graph (V₁)', f'{ve:.2f} mL'],
        ['Normality of NaOH (N₁)', f'{norm_naoh} N'],
        ['Volume of HCl taken (V₂)', f'{vol_acid} mL'],
        ['Normality of HCl (N₂)', f'{norm_hcl:.4f} N'],
        ['Amount of HCl', f'{amount_hcl:.4f} g/L'],
    ]
    rt = Table(result_table, colWidths=[280, 170])
    rt.setStyle(get_standard_table_style())
    elements.append(rt)

    doc.build(elements)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name=f"Exp5_{reg_number}.pdf", mimetype='application/pdf')

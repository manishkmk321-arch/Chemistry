from flask import Blueprint, render_template, request, session, redirect, url_for, send_file
import json
import io
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

exp8_bp = Blueprint('exp8', __name__)

MARK_HOUWINK = {
    "polystyrene": {"K": 1.1e-4, "a": 0.73, "polymer": "Polystyrene"},
    "pmma": {"K": 5.5e-4, "a": 0.76, "polymer": "PMMA"},
    "pvc": {"K": 6.3e-4, "a": 0.62, "polymer": "PVC"},
    "polyethylene": {"K": 6.2e-4, "a": 0.70, "polymer": "Polyethylene"},
    "polypropylene": {"K": 1.5e-4, "a": 0.75, "polymer": "Polypropylene"}
}

@exp8_bp.route('/')
def index():
    return render_template('exp8/polymer.html')

@exp8_bp.route('/calculate', methods=['POST'])
def calculate():
    t0 = float(request.form.get('t0'))
    concentrations = [float(c) for c in request.form.getlist('concentrations')]
    flow_times = [float(t) for t in request.form.getlist('flow_times')]
    polymer_system = request.form.get('polymer_system')
    system = MARK_HOUWINK[polymer_system]
    
    if len(concentrations) < 3 or len(flow_times) < 3:
        return render_template('exp8/polymer.html', error="Please enter at least 3 readings")
    
    data = []
    for c, t in zip(concentrations, flow_times):
        eta_r = t / t0
        eta_sp = eta_r - 1
        eta_red = eta_sp / c
        data.append({
            "conc": c, 
            "eta_r": round(eta_r, 4), 
            "eta_sp": round(eta_sp, 4), 
            "eta_red": round(eta_red, 4)
        })
    
    x = [d["conc"] for d in data]
    y = [d["eta_red"] for d in data]
    
    n = len(x)
    sum_x = sum(x)
    sum_y = sum(y)
    sum_xy = sum(xi * yi for xi, yi in zip(x, y))
    sum_x2 = sum(xi * xi for xi in x)
    
    slope = (n * sum_xy - sum_x * sum_y) / (n * sum_x2 - sum_x * sum_x)
    intercept = (sum_y - slope * sum_x) / n
    
    intrinsic_viscosity = intercept
    molecular_weight = (intrinsic_viscosity / system["K"]) ** (1 / system["a"])
    
    trend_line = [slope * xi + intercept for xi in x]
    
    return render_template('exp8/polymer_result.html',
                         data=data, 
                         concentrations=x, 
                         eta_red=y,
                         trend_line=trend_line,
                         intrinsic=round(intrinsic_viscosity, 4),
                         K=system["K"],
                         a_val=system["a"],
                         mw=round(molecular_weight, 2),
                         polymer=system["polymer"])

@exp8_bp.route('/download_pdf', methods=['POST'])
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
    
    styles, title_style, h2_style, normal_style, calc_style = get_standard_styles()
    
    elements = []
    
    add_pdf_header(elements, 'exp8', datetime.now().strftime('%d-%m-%Y'), student_name, reg_number, title_style, normal_style)
    
    elements.append(Paragraph("OBSERVATION TABLE", h2_style))
    
    if table_data:
        table_list = [['S.N.', 'Concentration\nC (g/dL)', 'Flow time\n(t sec)', 'Relative\nviscosity (ηr)', 'Specific\nviscosity (ηsp)', 'Reduced\nviscosity (ηred)']]
        for i, row in enumerate(table_data, 1):
            table_list.append([
                str(i),
                str(row.get('conc', '')),
                str(row.get('flow_time', '')),
                str(row.get('eta_r', '')),
                str(row.get('eta_sp', '')),
                str(row.get('eta_red', ''))
            ])
        
        col_widths = [30, 70, 70, 80, 80, 80]
        t = Table(table_list, colWidths=col_widths)
        t.setStyle(get_standard_table_style())
        elements.append(t)
        elements.append(Spacer(1, 15))
    
    if include_graph:
        concentrations = result_data.get('concentrations', [])
        data = result_data.get('data', [])
        trend_line = result_data.get('trend_line', [])
        
        eta_red = [d.get('eta_red', 0) for d in data]
        
        if concentrations and eta_red:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            
            fig, ax = plt.subplots(figsize=(7, 4.5))
            
            ax.plot(concentrations, eta_red, 'r-o', markersize=5, label='Reduced Viscosity')
            if trend_line:
                ax.plot(concentrations, trend_line, 'b--', linewidth=1.5, label='Trend Line')
            ax.set_xlabel('Concentration C (g/dL)', fontsize=11)
            ax.set_ylabel('Reduced Viscosity (ηred)', fontsize=11)
            ax.set_title('Reduced viscosity vs Concentration', fontsize=12, fontweight='bold')
            ax.legend()
            ax.grid(True, alpha=0.3)
            
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close(fig)
            
            elements.append(Image(img_buffer, width=400, height=240))
            elements.append(Spacer(1, 15))
    
    elements.append(Paragraph("CALCULATION", h2_style))
    
    polymer_name = result_data.get('polymer_name', '')
    t0 = result_data.get('t0', 0)
    K = result_data.get('K', 0)
    a_val = result_data.get('a_val', 0)
    intrinsic = result_data.get('intrinsic', 0)
    molecular_weight = result_data.get('molecular_weight', 0)
    
    elements.append(Paragraph(f"Intrinsic Viscosity [η] = {intrinsic:.4f} dL/g", normal_style))
    elements.append(Paragraph(f"Molecular Weight M = ([η] / K)<sup>1/a</sup> = ({intrinsic:.4f} / {K})<sup>1/{a_val}</sup> = {molecular_weight:.2f} g/mol", calc_style))
    elements.append(Spacer(1, 15))
    
    elements.append(Paragraph("FINAL RESULT", h2_style))
    result_table = Table([
        ['Intrinsic Viscosity [η]', f'{intrinsic:.4f} dL/g'],
        ['Molecular Weight (M)', f'{molecular_weight:.2f} g/mol']
    ], colWidths=[250, 150])
    result_table.setStyle(get_standard_table_style())
    elements.append(result_table)
    
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name=f"Exp8_{reg_number}.pdf", mimetype='application/pdf')

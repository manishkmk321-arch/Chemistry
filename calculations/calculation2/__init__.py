from flask import Blueprint, render_template, request, send_file
import io
import json
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime

exp2_bp = Blueprint('exp2', __name__)

@exp2_bp.route('/')
def index():
    return render_template('exp2/index.html')

@exp2_bp.route('/calculate', methods=['POST'])
def calculate():
    result_data = request.form.get('result_data')
    if result_data:
        return {'status': 'success', 'data': json.loads(result_data)}
    return {'status': 'error'}

@exp2_bp.route('/download_pdf', methods=['POST'])
def download_pdf():
    from calculations.pdf_utils import get_standard_styles, add_pdf_header, get_standard_table_style
    result_data = json.loads(request.form.get('result_data', '{}'))
    table_data = json.loads(request.form.get('table_data', '{}'))
    student_name = request.form.get('student_name', '')
    reg_number = request.form.get('reg_number', '')
    
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)
    
    styles, title_style, h2_style, normal_style, calc_style, header_style, subheader_style = get_standard_styles()
    
    elements = []
    
    add_pdf_header(elements, 'exp2', datetime.now().strftime('%d-%m-%Y'), student_name, reg_number, title_style, normal_style, header_style, subheader_style)
    
    # ROUGH TITRATION TABLE
    elements.append(Paragraph("ROUGH TITRATION TABLE", h2_style))
    if table_data.get('t1'):
        table_list = [['S.N.', 'Initial Reading\n(ml)', 'Final Reading\n(ml)', 'Volume of AgNO3\nUsed (ml)']]
        for i, row in enumerate(table_data['t1'], 1):
            table_list.append([str(i), str(row.get('initial', '')), str(row.get('final', '')), str(row.get('volume', ''))])
        
        t = Table(table_list, colWidths=[40, 110, 110, 140])
        t.setStyle(get_standard_table_style())
        elements.append(t)
        elements.append(Spacer(1, 15))
    else:
        elements.append(Paragraph("- No rough titration readings -", normal_style))
        elements.append(Spacer(1, 15))
        
    # FAIR TITRATION TABLE
    elements.append(Paragraph("FAIR TITRATION TABLE", h2_style))
    if table_data.get('t2'):
        table_list = [['S.N.', 'Initial Reading\n(ml)', 'Final Reading\n(ml)', 'Volume of AgNO3\nUsed (ml)', 'Concordant\nValue']]
        v_concordant = float(result_data.get('v2', 0))
        for i, row in enumerate(table_data['t2'], 1):
            vol = float(row.get('volume', 0))
            is_concordant = abs(vol - v_concordant) < 0.01 if v_concordant > 0 else False
            # Find index of min volume matching concordant logic
            vols = [float(r.get('volume', 0)) for r in table_data['t2']]
            min_idx = vols.index(min([v for v in vols if v > 0])) if any(v > 0 for v in vols) else -1
            concordant_val = str(round(v_concordant, 2)) if is_concordant and i - 1 == min_idx else '-'
            table_list.append([str(i), str(row.get('initial', '')), str(row.get('final', '')), str(row.get('volume', '')), concordant_val])
        
        t = Table(table_list, colWidths=[40, 90, 90, 100, 80])
        t.setStyle(get_standard_table_style())
        elements.append(t)
        elements.append(Spacer(1, 15))
    else:
        elements.append(Paragraph("- No fair titration readings -", normal_style))
        elements.append(Spacer(1, 15))
        
    elements.append(Paragraph("CALCULATIONS", h2_style))
    elements.append(Paragraph("Formula: N(Sample) = (N(AgNO3) × V(AgNO3)) / V(Sample)", normal_style))
    elements.append(Paragraph(f"         = ({result_data.get('normAgno3', 0):.4f} × {result_data.get('v2', 0):.2f}) / {result_data.get('sampleVol', 0)}", calc_style))
    elements.append(Paragraph(f"         = {result_data.get('normSample', 0):.4f} N", calc_style))
    elements.append(Spacer(1, 10))
    
    elements.append(Paragraph("Formula: Amount of Chloride = N × 1000 × 35.45", normal_style))
    elements.append(Paragraph(f"         = {result_data.get('normSample', 0):.4f} × 1000 × 35.45", calc_style))
    elements.append(Paragraph(f"         = {result_data.get('chlorideAmount', 0):.2f} mg/L", calc_style))
    elements.append(Spacer(1, 15))
    
    elements.append(Paragraph("FINAL RESULT", h2_style))
    elements.append(Paragraph(f"The Normality of Sample is {result_data.get('normSample', 0):.4f} N", normal_style))
    elements.append(Paragraph(f"The Amount of Chloride is {result_data.get('chlorideAmount', 0):.2f} mg/L", normal_style))
    
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name=f"Exp2_{reg_number}.pdf", mimetype='application/pdf')

@exp2_bp.route('/reset')
def reset():
    return render_template('exp2/index.html')
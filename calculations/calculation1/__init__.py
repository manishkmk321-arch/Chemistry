from flask import Blueprint, render_template, request, session, redirect, url_for, send_file
import json
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from datetime import datetime

exp1_bp = Blueprint('exp1', __name__)

@exp1_bp.route('/')
def index():
    return render_template('exp1/index.html')

@exp1_bp.route('/calculate', methods=['POST'])
def calculate():
    result_data = request.form.get('result_data')
    if result_data:
        session['result_data'] = json.loads(result_data)
    return redirect(url_for('exp1.index'))

@exp1_bp.route('/download_pdf', methods=['POST'])
def download_pdf():
    from calculations.pdf_utils import get_standard_styles, add_pdf_header, get_standard_table_style
    result_data = json.loads(request.form.get('result_data', '{}'))
    table_data = json.loads(request.form.get('table_data', '{}'))
    student_name = request.form.get('student_name', '')
    reg_number = request.form.get('reg_number', '')
    experiment_title = request.form.get('experiment_title', '') # Just in case

    sample_vol = result_data.get('vs', 20)
    boiled_vol = result_data.get('vb', 20)
    indicator = "EBT"

    filename = f"Experiment1_{student_name}_{reg_number}.pdf"

    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=A4, rightMargin=50, leftMargin=50, topMargin=50, bottomMargin=50)

    styles, title_style, h2_style, normal_style, calc_style, header_style, subheader_style = get_standard_styles()

    elements = []

    add_pdf_header(elements, 'exp1', datetime.now().strftime('%d-%m-%Y'), student_name, reg_number, title_style, normal_style, header_style, subheader_style)

    def add_table(title, data, v_concordant, sample_volume, elements):
        if not data:
            return
        elements.append(Paragraph(title, h2_style))
        table_rows = [['S.N.', 'Volume taken\n(ml)', 'Initial', 'Final', 'Volume of\nEDTA (ml)', 'Concordant\nValue', 'Indicator']]
        for i in range(len(data)):
            vol = float(data[i]['volume'])
            is_concordant = abs(vol - v_concordant) < 0.01 if v_concordant > 0 else False
            concordant_val = str(round(v_concordant, 2)) if is_concordant and i == data.index(min(data, key=lambda x: float(x['volume']))) else '-'
            table_rows.append([
                str(i + 1),
                str(sample_volume),
                data[i]['initial'],
                data[i]['final'],
                data[i]['volume'],
                concordant_val,
                indicator
            ])
        t = Table(table_rows, colWidths=[35, 75, 55, 55, 65, 70, 70])
        t.setStyle(get_standard_table_style())
        elements.append(t)
        elements.append(Spacer(1, 15))

    add_table("TITRATION 1 – STANDARD HARD WATER", table_data.get('t1', []), result_data.get('v1', 0), 20, elements)
    add_table("TITRATION 2 – SAMPLE HARD WATER", table_data.get('t2', []), result_data.get('v2', 0), sample_vol, elements)
    add_table("TITRATION 3 – BOILED HARD WATER", table_data.get('t3', []), result_data.get('v3', 0), boiled_vol, elements)

    elements.append(Paragraph("CALCULATIONS:", h2_style))
    elements.append(Paragraph(f"Concordant Value V1 (Titration 1) = {result_data.get('v1', 0):.2f} ml", normal_style))
    elements.append(Paragraph(f"Concordant Value V2 (Titration 2) = {result_data.get('v2', 0):.2f} ml", normal_style))
    elements.append(Paragraph(f"Concordant Value V3 (Titration 3) = {result_data.get('v3', 0):.2f} ml", normal_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Formula: Total Hardness = (V2 × 1000 / Vs) × (20 / V1)", normal_style))
    elements.append(Paragraph(f"         = ({result_data.get('v2', 0):.2f} × 1000 / {sample_vol}) × (20 / {result_data.get('v1', 0):.2f})", calc_style))
    elements.append(Paragraph(f"         = {result_data.get('totalHardness', 0):.2f} ppm", calc_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Formula: Permanent Hardness = (V3 × 1000 / Vb) × (20 / V1)", normal_style))
    elements.append(Paragraph(f"         = ({result_data.get('v3', 0):.2f} × 1000 / {boiled_vol}) × (20 / {result_data.get('v1', 0):.2f})", calc_style))
    elements.append(Paragraph(f"         = {result_data.get('permanentHardness', 0):.2f} ppm", calc_style))
    elements.append(Spacer(1, 10))

    elements.append(Paragraph("Formula: Temporary Hardness = Total Hardness - Permanent Hardness", normal_style))
    elements.append(Paragraph(f"         = {result_data.get('totalHardness', 0):.2f} - {result_data.get('permanentHardness', 0):.2f}", calc_style))
    elements.append(Paragraph(f"         = {result_data.get('temporaryHardness', 0):.2f} ppm", calc_style))
    elements.append(Spacer(1, 15))

    elements.append(Paragraph("FINAL RESULT", h2_style))
    elements.append(Paragraph(f"The Total Hardness is {result_data.get('totalHardness', 0):.2f} ppm", normal_style))
    elements.append(Paragraph(f"The Permanent Hardness is {result_data.get('permanentHardness', 0):.2f} ppm", normal_style))
    elements.append(Paragraph(f"The Temporary Hardness is {result_data.get('temporaryHardness', 0):.2f} ppm", normal_style))

    doc.build(elements)
    buffer.seek(0)

    return send_file(buffer, as_attachment=True, download_name=filename, mimetype='application/pdf')

@exp1_bp.route('/reset')
def reset():
    session.clear()
    return redirect(url_for('exp1.index'))
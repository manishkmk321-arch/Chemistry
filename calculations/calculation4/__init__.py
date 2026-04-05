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

exp4_bp = Blueprint('exp4', __name__)

@exp4_bp.route('/')
def index():
    return render_template('exp4/ph_meter.html')

@exp4_bp.route('/download_pdf', methods=['POST'])
def download_pdf():
    from calculations.pdf_utils import get_standard_styles, add_pdf_header, get_standard_table_style
    # Safe JSON parsing — never crash on empty or invalid data
    result_data_raw = request.form.get('result_data')
    try:
        result_data = json.loads(result_data_raw) if result_data_raw and result_data_raw.strip() else {}
    except Exception:
        result_data = {}

    table_data_raw = request.form.get('table_data')
    print("Received table_data:", table_data_raw)  # Debug
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
    
    add_pdf_header(elements, 'exp4', datetime.now().strftime('%d-%m-%Y'), student_name, reg_number, title_style, normal_style, header_style, subheader_style)
    
    elements.append(Paragraph("OBSERVATION TABLE", h2_style))
    
    if table_data:
        table_list = [['S.N.', 'Volume of NaOH\nAdded (mL)', 'pH', 'ΔpH', 'ΔV', 'ΔpH/ΔV', 'Average\nVolume (mL)']]
        for i, row in enumerate(table_data, 1):
            dph = row.get('dph', '-') if row.get('dph') != 'None' and row.get('dph') is not None else '-'
            dv = row.get('dv', '-') if row.get('dv') != 'None' and row.get('dv') is not None else '-'
            dphdv = row.get('dphdv', '-') if row.get('dphdv') != 'None' and row.get('dphdv') is not None else '-'
            avg = row.get('avgVol', '-') if row.get('avgVol') != 'None' and row.get('avgVol') is not None else '-'
            table_list.append([str(i), str(row.get('volume', '')), str(row.get('ph', '')), str(dph), str(dv), str(dphdv), str(avg)])
        
        col_widths = [30, 85, 50, 50, 50, 70, 85]
        t = Table(table_list, colWidths=col_widths)
        t.setStyle(get_standard_table_style())
        elements.append(t)
        elements.append(Spacer(1, 15))
    
    if include_graph:
        volumes = result_data.get('volumes', [])
        phValues = result_data.get('phValues', [])
        v1 = result_data.get('v1', 0)
        
        if volumes and phValues:
            fig1, ax1 = plt.subplots(figsize=(7, 4.5))
            ax1.plot(volumes, phValues, 'b-o', markersize=5)
            ax1.axvline(x=v1, color='r', linestyle='--', linewidth=1.5, label=f'Equivalence Point ({v1:.2f} mL)')
            ax1.set_xlabel('Volume of NaOH (mL)', fontsize=11)
            ax1.set_ylabel('pH', fontsize=11)
            ax1.set_title('Graph 1: pH vs Volume of NaOH', fontsize=12, fontweight='bold')
            ax1.legend(fontsize=9)
            ax1.grid(True, alpha=0.3)
            
            img_buffer1 = io.BytesIO()
            plt.savefig(img_buffer1, format='png', dpi=150, bbox_inches='tight')
            img_buffer1.seek(0)
            plt.close(fig1)
            
            elements.append(Image(img_buffer1, width=400, height=240))
            elements.append(Spacer(1, 15))
            
            calcData = result_data.get('calcData', [])
            avgVols = [r['avgVol'] for r in calcData if r.get('avgVol') is not None]
            dphdvVals = [r['dphdv'] for r in calcData if r.get('dphdv') is not None]
            
            if avgVols and dphdvVals:
                fig2, ax2 = plt.subplots(figsize=(7, 4.5))
                ax2.plot(avgVols, dphdvVals, 'r-o', markersize=5)
                ax2.set_xlabel('Average Volume (mL)', fontsize=11)
                ax2.set_ylabel('ΔpH/ΔV', fontsize=11)
                ax2.set_title('Graph 2: ΔpH/ΔV vs Average Volume', fontsize=12, fontweight='bold')
                ax2.grid(True, alpha=0.3)
                
                img_buffer2 = io.BytesIO()
                plt.savefig(img_buffer2, format='png', dpi=150, bbox_inches='tight')
                img_buffer2.seek(0)
                plt.close(fig2)
                
                elements.append(Image(img_buffer2, width=400, height=240))
                elements.append(Spacer(1, 15))
    
    elements.append(Paragraph("CALCULATIONS", h2_style))
    elements.append(Paragraph("Formula: ΔpH = pH₂ − pH₁", normal_style))
    elements.append(Paragraph("Formula: ΔV = V₂ − V₁", normal_style))
    elements.append(Paragraph("Formula: ΔpH/ΔV = ΔpH ÷ ΔV", normal_style))
    elements.append(Spacer(1, 10))
    
    elements.append(Paragraph(f"Equivalence point (maximum ΔpH/ΔV) = {result_data.get('v1', 0):.2f} mL", normal_style))
    elements.append(Spacer(1, 10))
    
    elements.append(Paragraph("Formula: N₂ = (N₁ × V₁) / V₂", normal_style))
    elements.append(Paragraph(f"         = ({result_data.get('normNaoh', 0)} × {result_data.get('v1', 0):.2f}) / {result_data.get('volAcid', 0)}", calc_style))
    elements.append(Paragraph(f"         = {result_data.get('n2', 0):.4f} N", calc_style))
    elements.append(Spacer(1, 10))
    
    elements.append(Paragraph("Formula: Amount of HCl = N₂ × 36.45", normal_style))
    elements.append(Paragraph(f"         = {result_data.get('n2', 0):.4f} × 36.45", calc_style))
    elements.append(Paragraph(f"         = {result_data.get('amountHcl', 0):.4f} g/L", calc_style))
    elements.append(Spacer(1, 15))
    
    elements.append(Paragraph("FINAL RESULT", h2_style))
    elements.append(Paragraph(f"The Strength of HCl is {result_data.get('n2', 0):.4f} N", normal_style))
    elements.append(Paragraph(f"The Amount of HCl is {result_data.get('amountHcl', 0):.4f} g/L", normal_style))
    
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name=f"Exp4_{reg_number}.pdf", mimetype='application/pdf')
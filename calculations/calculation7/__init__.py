from flask import Blueprint, render_template, request, session, redirect, url_for, send_file
import json
import io
from datetime import datetime
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table, TableStyle, Image
from reportlab.lib.pagesizes import A4
from reportlab.lib import colors

exp7_bp = Blueprint('exp7', __name__)

@exp7_bp.route('/')
def index():
    return render_template('exp7/potentiometry.html')

@exp7_bp.route('/download_pdf', methods=['POST'])
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
    
    add_pdf_header(elements, 'exp7', datetime.now().strftime('%d-%m-%Y'), student_name, reg_number, title_style, normal_style, header_style, subheader_style)
    
    elements.append(Paragraph("OBSERVATION TABLE", h2_style))
    
    if table_data:
        table_list = [['S.N.', 'Volume of KMnO₄\n(mL)', 'EMF\n(millivolt)', 'ΔE', 'ΔV', 'ΔE/ΔV']]
        for i, row in enumerate(table_data, 1):
            table_list.append([
                str(i),
                str(row.get('volume', '')),
                str(row.get('emf', '')),
                str(row.get('de', '')),
                str(row.get('dv', '')),
                str(row.get('dedv', ''))
            ])
        
        col_widths = [30, 80, 100, 60, 60, 80]
        t = Table(table_list, colWidths=col_widths)
        t.setStyle(get_standard_table_style())
        elements.append(t)
        elements.append(Spacer(1, 15))
    
    if include_graph:
        fair_volumes = result_data.get('fair_volumes', [])
        fair_emf = result_data.get('fair_emf', [])
        dedv_volumes = result_data.get('dedv_volumes', [])
        dedv_data = result_data.get('dedv_data', [])
        v1_val = result_data.get('v1', 0)
        
        if fair_volumes and fair_emf:
            import matplotlib
            matplotlib.use('Agg')
            import matplotlib.pyplot as plt
            
            fig, (ax1, ax2) = plt.subplots(2, 1, figsize=(7, 6))
            
            ax1.plot(fair_volumes, fair_emf, 'b-o', markersize=5, label='EMF')
            ax1.set_xlabel('Volume of KMnO₄ (mL)', fontsize=11)
            ax1.set_ylabel('EMF (millivolt)', fontsize=11)
            ax1.set_title('EMF vs Volume of KMnO₄', fontsize=12, fontweight='bold')
            ax1.legend()
            ax1.grid(True, alpha=0.3)
            
            if dedv_volumes and dedv_data:
                ax2.plot(dedv_volumes, dedv_data, 'r-o', markersize=5, label='ΔE/ΔV')
                ax2.axvline(x=v1_val, color='purple', linestyle=':', linewidth=1.5, label=f'Equivalence Point ({v1_val:.2f} mL)')
                ax2.set_xlabel('Volume of KMnO₄ (mL)', fontsize=11)
                ax2.set_ylabel('ΔE/ΔV', fontsize=11)
                ax2.set_title('ΔE/ΔV vs Volume of KMnO₄', fontsize=12, fontweight='bold')
                ax2.legend()
                ax2.grid(True, alpha=0.3)
            
            plt.tight_layout()
            
            img_buffer = io.BytesIO()
            plt.savefig(img_buffer, format='png', dpi=150, bbox_inches='tight')
            img_buffer.seek(0)
            plt.close(fig)
            
            elements.append(Image(img_buffer, width=400, height=320))
            elements.append(Spacer(1, 15))
    
    elements.append(Paragraph("CALCULATION", h2_style))
    
    v1 = result_data.get('v1', 0)
    N1 = result_data.get('N1', 0)
    V2 = result_data.get('V2', 0)
    N2 = result_data.get('N2', 0)
    amount_fe = result_data.get('Amount_Fe', 0)
    
    elements.append(Paragraph(f"N₂ = (N₁ × V₁) / V₂ = ({N1:.4f} × {v1:.2f}) / {V2:.2f} = {N2:.4f} N", calc_style))
    elements.append(Paragraph(f"Amount of Ferrous ion = N₂ × 55.85 × 100 / 1000 = ({N2:.4f} × 55.85 × 100) / 1000 = {amount_fe:.4f} g/L", calc_style))
    elements.append(Spacer(1, 15))
    
    elements.append(Paragraph("FINAL RESULT", h2_style))
    result_table = Table([
        ['Equivalence Volume (V1)', f'{v1:.2f} mL'],
        ['Strength of FAS (N₂)', f'{N2:.4f} N'],
        ['Amount of Ferrous ion', f'{amount_fe:.4f} g/L']
    ], colWidths=[250, 150])
    result_table.setStyle(get_standard_table_style())
    elements.append(result_table)
    
    doc.build(elements)
    buffer.seek(0)
    
    return send_file(buffer, as_attachment=True, download_name=f"Exp7_{reg_number}.pdf", mimetype='application/pdf')

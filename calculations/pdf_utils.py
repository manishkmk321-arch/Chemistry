import io
import os
import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
from reportlab.platypus import Paragraph, Spacer, Table, TableStyle, Image, HRFlowable
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib import colors
from reportlab.lib.utils import ImageReader

EXPERIMENTS_DATA = [
    {"id": 1, "name": "DETERMINATION OF HARDNESS (Ca²⁺) OF WATER USING EDTA COMPLEXOMETRY METHOD", "slug": "exp1"},
    {"id": 2, "name": "ESTIMATION OF AMOUNT OF CHLORIDE CONTENT OF A WATER SAMPLE", "slug": "exp2"},
    {"id": 3, "name": "DETERMINATION OF THE AMOUNT OF SODIUM CARBONATE AND SODIUM HYDROXIDE IN A MIXTURE BY TITRATION", "slug": "exp3"},
    {"id": 4, "name": "DETERMINATION OF STRENGTH OF AN ACID USING pH METER", "slug": "exp4"},
    {"id": 5, "name": "DETERMINATION OF STRENGTH OF AN ACID BY CONDUCTOMETRY", "slug": "exp5"},
    {"id": 6, "name": "DETERMINATION OF THE STRENGTH OF A MIXTURE OF ACETIC ACID AND HYDROCHLORIC ACID BY CONDUCTOMETRY", "slug": "exp6"},
    {"id": 7, "name": "DETERMINATION OF FERROUS ION USING POTASSIUM DICHROMATE BY POTENTIOMETRIC TITRATION", "slug": "exp7"},
    {"id": 8, "name": "DETERMINATION OF MOLECULAR WEIGHT OF A POLYMER BY VISCOSITY AVERAGE METHOD", "slug": "exp8"}
]

def get_experiment_title(slug):
    for exp in EXPERIMENTS_DATA:
        if exp['slug'] == slug:
            return exp['name'].upper()
    return "EXPERIMENT TITLE"

def get_standard_styles():
    styles = getSampleStyleSheet()
    title_style = ParagraphStyle(
        'TitleStyle', parent=styles['Heading1'], fontName='Helvetica-Bold', fontSize=14, alignment=1, spaceAfter=20
    )
    h2_style = ParagraphStyle(
        'H2', parent=styles['Heading2'], fontName='Helvetica-Bold', fontSize=12, spaceBefore=15, spaceAfter=10
    )
    normal_style = styles['Normal']
    normal_style.fontSize = 11
    normal_style.spaceAfter = 6
    calc_style = ParagraphStyle(
        'CalcStyle', parent=normal_style, fontName='Helvetica', fontSize=11, spaceBefore=2, spaceAfter=2, leftIndent=20
    )
    header_style = ParagraphStyle(
        'HeaderStyle', parent=styles['Normal'], fontName='Helvetica-Bold', fontSize=11, alignment=1, spaceAfter=3
    )
    subheader_style = ParagraphStyle(
        'SubHeaderStyle', parent=styles['Normal'], fontName='Helvetica', fontSize=10, alignment=1, spaceAfter=3
    )
    return styles, title_style, h2_style, normal_style, calc_style, header_style, subheader_style

def add_pdf_header(elements, slug, date_str, name, reg_no, title_style, normal_style, header_style=None, subheader_style=None):
    title = get_experiment_title(slug)
    
    logo_path = os.path.join(os.path.dirname(__file__), '..', 'static', 'logo.png')
    
    if header_style and subheader_style:
        if os.path.exists(logo_path):
            logo = Image(logo_path, width=50, height=50)
            elements.append(Spacer(1, 10))
            
            title_para = Paragraph("SRM Institute of Science and Technology, Tiruchirappalli", header_style)
            subtitle_para = Paragraph("Faculty of Engineering and Technology", subheader_style)
            dept_para = Paragraph("Department of Chemistry", subheader_style)
            
            header_table = Table([[logo, title_para]], colWidths=[60, 400])
            header_table.setStyle(TableStyle([
                ('VALIGN', (0, 0), (-1, -1), 'MIDDLE'),
                ('ALIGN', (0, 0), (0, 0), 'LEFT'),
                ('ALIGN', (1, 0), (1, 0), 'CENTER'),
            ]))
            elements.append(header_table)
            elements.append(subtitle_para)
            elements.append(dept_para)
            elements.append(Spacer(1, 15))
        else:
            elements.append(Paragraph("SRM Institute of Science and Technology, Tiruchirappalli", header_style))
            elements.append(Paragraph("Faculty of Engineering and Technology", subheader_style))
            elements.append(Paragraph("Department of Chemistry", subheader_style))
            elements.append(Spacer(1, 15))
    
    elements.append(Paragraph(title, title_style))
    elements.append(Paragraph(f"Date: {date_str}", normal_style))
    elements.append(Paragraph(f"Name: {name}", normal_style))
    elements.append(Paragraph(f"Registration No: {reg_no}", normal_style))
    elements.append(Spacer(1, 10))
    elements.append(HRFlowable(width="100%", thickness=1, color=colors.black, spaceBefore=0, spaceAfter=15))

def get_standard_table_style():
    return TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.lightgrey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.black),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('FONTSIZE', (0, 0), (-1, -1), 10),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 10),
        ('GRID', (0, 0), (-1, -1), 0.5, colors.black),
    ])

def create_graph(x_data, y_data, x_label, y_label, title=""):
    plt.figure(figsize=(6, 4))
    plt.plot(x_data, y_data, marker='o', linestyle='-', color='b')
    plt.xlabel(x_label)
    plt.ylabel(y_label)
    if title:
        plt.title(title)
    plt.grid(True)
    
    img_buffer = io.BytesIO()
    plt.savefig(img_buffer, format='png', bbox_inches='tight')
    plt.close()
    img_buffer.seek(0)
    return Image(img_buffer, width=400, height=270)

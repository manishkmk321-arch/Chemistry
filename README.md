# Chemistry Lab Web Application

A comprehensive digital chemistry laboratory system designed to simplify and modernize traditional lab work. This web application provides an interactive platform where students can perform virtual experiments, record observations, carry out calculations, and generate professional lab reports automatically.

---

## 📋 Project Overview

This project transforms traditional chemistry laboratory practices into a smart digital system. With 8 different experiments covered, students can conduct virtual experiments, automatically calculate results, visualize data with graphs, and generate professional PDF reports - all in one place.

### 🎯 Objective

- Eliminate manual calculation errors
- Reduce paperwork
- Provide a smart, user-friendly environment for conducting chemistry experiments digitally
- Generate professional lab reports matching real laboratory standards

---

## 🧪 Supported Experiments

The application includes 8 major chemistry experiments:

| # | Experiment Name |
|---|-----------------|
| 1 | **DETERMINATION OF HARDNESS (Ca²⁺) OF WATER USING EDTA COMPLEXOMETRY METHOD** |
| 2 | **ESTIMATION OF AMOUNT OF CHLORIDE CONTENT OF A WATER SAMPLE** |
| 3 | **DETERMINATION OF THE AMOUNT OF SODIUM CARBONATE AND SODIUM HYDROXIDE IN A MIXTURE BY TITRATION** |
| 4 | **DETERMINATION OF STRENGTH OF AN ACID USING pH METER** |
| 5 | **DETERMINATION OF STRENGTH OF AN ACID BY CONDUCTOMETRY** |
| 6 | **DETERMINATION OF THE STRENGTH OF A MIXTURE OF ACETIC ACID AND HYDROCHLORIC ACID BY CONDUCTOMETRY** |
| 7 | **DETERMINATION OF FERROUS ION USING POTASSIUM DICHROMATE BY POTENTIOMETRIC TITRATION** |
| 8 | **DETERMINATION OF MOLECULAR WEIGHT OF A POLYMER BY VISCOSITY AVERAGE METHOD** |

---

## 🚀 Key Features

### 1. Multiple Experiment Support
Each experiment is structured according to standard lab procedures with proper titration steps.

### 2. Dynamic Table Generation
- Users can select the number of readings
- Tables are generated dynamically based on input
- All input fields start empty with placeholders
- Calculated fields (ΔpH, ΔV, ΔpH/ΔV, Average Volume, etc.) are auto-computed

### 3. Automatic Calculations
- Step-by-step calculations
- Concordant value detection
- Average calculations
- Formula-based result generation

### 4. Edit Values Feature
- Users can modify entered values even after calculation
- No need to restart the experiment
- Recalculation happens instantly

### 5. Graph Generation
For relevant experiments, graphs are automatically plotted:
- pH vs Volume
- Conductance vs Volume
- EMF vs Volume
- ΔE/ΔV vs Volume
- Reduced viscosity vs Concentration

### 6. Professional PDF Report Generation
Users can download complete lab reports including:
- Experiment Title (auto-fetched and uppercase)
- Date, Name, Registration Number
- Institution header with logo (SRM Institute of Science and Technology)
- Observation Tables
- Graphs
- Step-by-step Calculations
- Final Result

### 7. Consistent UI & Table Design
- Uniform table format across all experiments
- Proper borders, alignment, and formatting
- Clean and professional interface
- Responsive design for all devices

### 8. Error Handling & Data Safety
- Handles empty or incorrect inputs safely
- Prevents crashes during calculations and PDF generation
- Ensures smooth user experience

---

## 🛠️ Technologies Used

### Frontend
- **HTML5** - Structure
- **CSS3** - Styling (Responsive design)
- **JavaScript** - Client-side logic and interactivity
- **Chart.js** - Graph generation
- **Font Awesome** - Icons

### Backend
- **Python** - Server-side programming
- **Flask** - Web framework

### Libraries
- **ReportLab** - PDF generation
- **Matplotlib** - Graph plotting for PDFs

---

## 📂 Project Structure

```
chemistry_lab_website/
├── app.py                    # Main Flask application
├── calculations/             # Backend calculation modules
│   ├── __init__.py
│   ├── calculation1/         # Experiment 1 - EDTA Hardness
│   ├── calculation2/         # Experiment 2 - Chloride Estimation
│   ├── calculation3/         # Experiment 3 - Na2CO3 + NaOH
│   ├── calculation4/         # Experiment 4 - pH Meter
│   ├── calculation5/         # Experiment 5 - Conductometry
│   ├── calculation6/         # Experiment 6 - Mixture Conductometry
│   ├── calculation7/         # Experiment 7 - Potentiometry
│   ├── calculation8/         # Experiment 8 - Polymer Viscosity
│   └── pdf_utils.py          # PDF generation utilities
├── templates/               # HTML templates
│   ├── partials/            # Reusable components (header)
│   ├── exp1/                # Experiment 1 templates
│   ├── exp2/                # Experiment 2 templates
│   ├── exp3/                # Experiment 3 templates
│   ├── exp4/                # Experiment 4 templates
│   ├── exp5/                # Experiment 5 templates
│   ├── exp6/                # Experiment 6 templates
│   ├── exp7/                # Experiment 7 templates
│   ├── exp8/                # Experiment 8 templates
│   ├── index.html           # Home page
│   ├── experiments.html      # Experiments list
│   └── view_pdf.html        # View PDF page
├── static/                  # Static files
│   ├── style.css            # Main stylesheet
│   ├── logo.png             # SRM Logo
│   ├── bibek.png            # Developer photo
│   └── Dipendra.png         # Developer photo
└── venv/                   # Virtual environment
```

---

## 💻 Installation & Setup

### Prerequisites
- Python 3.8 or higher
- pip package manager

### Installation Steps

1. **Clone the repository**
   ```bash
   cd chemistry_lab_website
   ```

2. **Create and activate virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Mac/Linux
   # or
   venv\Scripts\activate    # On Windows
   ```

3. **Install required packages**
   ```bash
   pip install flask reportlab matplotlib
   ```

4. **Run the application**
   ```bash
   python3 -m flask run
   ```

5. **Access the application**
   Open your browser and navigate to:
   ```
   http://127.0.0.1:5000
   ```

---

## 📱 How to Use

### For Students

1. **Select an Experiment**
   - Go to the home page
   - Click on "Calculations"
   - Choose your experiment

2. **Enter Data**
   - Fill in the required parameters (volume, normality, etc.)
   - Select number of readings
   - Generate tables
   - Enter burette readings

3. **Calculate Results**
   - Click "Calculate" button
   - View results and graphs

4. **Download Report**
   - Click "Download Full Report" or "Generate PDF"
   - Enter your name and registration number
   - Download your professional lab report

### For Viewing Existing Reports
- Click "View PDF" on the home page to view pre-generated reports

---

## 👥 Developers

### Team Members

| Name | Role | Contact |
|------|------|---------|
| **Bibek Khadka** | Backend (PDF Generation & Graph) | +91 8448582274 |
| **Dipendra Sah** | Frontend | +91 8757072401 |

### Contact for More Information
- **WhatsApp**: +977 9867154760

---

## 🔮 Future Enhancements

- Database integration (Firebase / SQL)
- User login system
- Cloud storage for reports
- AI-based error detection in experiments
- Mobile application
- Export to other formats (Word, Excel)

---

## 📝 License

This project is developed for educational purposes.

---

## 🙏 Acknowledgments

- **SRM Institute of Science and Technology, Tiruchirappalli**
- **Faculty of Engineering and Technology**
- **Department of Chemistry**

---

## 📌 Conclusion

This Chemistry Lab Web Application is a complete automation system that bridges the gap between traditional laboratory practices and modern technology. It makes experiments faster, more accurate, easy to manage, and professionally documented - highly useful for students, teachers, and educational institutions.

---

**Version**: 1.0  
**Last Updated**: April 2026
# Chemistry
# Chemistry
# Chemistry

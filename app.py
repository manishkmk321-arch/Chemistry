import os
<<<<<<< HEAD
from flask import Flask, render_template, send_file, redirect
=======
from flask import Flask, render_template, send_file, redirect 
>>>>>>> 289538a (Update view_pdf route to redirect to Google Drive)
from calculations.calculation1 import exp1_bp
from calculations.calculation2 import exp2_bp
from calculations.calculation3 import exp3_bp
from calculations.calculation4 import exp4_bp
from calculations.calculation5 import exp5_bp
from calculations.calculation6 import exp6_bp
from calculations.calculation7 import exp7_bp
from calculations.calculation8 import exp8_bp

app = Flask(__name__)
app.secret_key = "chemistry_lab_secret_key_123"

EXPERIMENTS = [
    {"id": 1, "name": "DETERMINATION OF HARDNESS (Ca²⁺) OF WATER USING EDTA COMPLEXOMETRY METHOD", "slug": "exp1"},
    {"id": 2, "name": "ESTIMATION OF AMOUNT OF CHLORIDE CONTENT OF A WATER SAMPLE", "slug": "exp2"},
    {"id": 3, "name": "DETERMINATION OF THE AMOUNT OF SODIUM CARBONATE AND SODIUM HYDROXIDE IN A MIXTURE BY TITRATION", "slug": "exp3"},
    {"id": 4, "name": "DETERMINATION OF STRENGTH OF AN ACID USING pH METER", "slug": "exp4"},
    {"id": 5, "name": "DETERMINATION OF STRENGTH OF AN ACID BY CONDUCTOMETRY", "slug": "exp5"},
    {"id": 6, "name": "DETERMINATION OF THE STRENGTH OF A MIXTURE OF ACETIC ACID AND HYDROCHLORIC ACID BY CONDUCTOMETRY", "slug": "exp6"},
    {"id": 7, "name": "DETERMINATION OF FERROUS ION USING POTASSIUM DICHROMATE BY POTENTIOMETRIC TITRATION", "slug": "exp7"},
    {"id": 8, "name": "DETERMINATION OF MOLECULAR WEIGHT OF A POLYMER BY VISCOSITY AVERAGE METHOD", "slug": "exp8"},
]

app.register_blueprint(exp1_bp, url_prefix="/exp1")
app.register_blueprint(exp2_bp, url_prefix="/exp2")
app.register_blueprint(exp3_bp, url_prefix="/exp3")
app.register_blueprint(exp4_bp, url_prefix="/exp4")
app.register_blueprint(exp5_bp, url_prefix="/exp5")
app.register_blueprint(exp6_bp, url_prefix="/exp6")
app.register_blueprint(exp7_bp, url_prefix="/exp7")
app.register_blueprint(exp8_bp, url_prefix="/exp8")

@app.route('/')
def index():
    return render_template('index.html', experiments=EXPERIMENTS)

@app.route('/view_pdf')
def view_pdf():
    # Google Drive preview link
    pdf_url = "https://drive.google.com/file/d/1oAKSQEotat3-estig18W2_i9f3Xj78yv/preview"
    return redirect(pdf_url)
<<<<<<< HEAD
    
=======

>>>>>>> 289538a (Update view_pdf route to redirect to Google Drive)
@app.route('/calculations')
def calculations():
    return render_template('experiments.html', experiments=EXPERIMENTS)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

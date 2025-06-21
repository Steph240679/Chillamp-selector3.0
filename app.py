from flask import Flask, render_template, request, jsonify, send_file
from preset_engine import get_presets_for_combination
from presets import presets
from fpdf2 import FPDF
import tempfile
import os

from flask import Flask
app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/bassistes')
def bassistes():
    noms = sorted([preset['nom'] for preset in presets])
    return jsonify(noms)

@app.route('/get_preset', methods=['POST'])
def get_preset():
    data = request.get_json()
    resultat = get_presets_for_combination(
        data.get("bassiste"),
        data.get("basse"),
        data.get("ampli"),
        data.get("baffle"),
        data.get("effets", [])
    )
    return jsonify(resultat)

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    data = request.form.to_dict(flat=False)
    bassiste = data.get("bassiste", [""])[0]
    basse = data.get("basse", [""])[0]
    ampli = data.get("ampli", [""])[0]
    baffle = data.get("baffle", [""])[0]
    effets = data.get("effets", [])

    preset = get_presets_for_combination(bassiste, basse, ampli, baffle, effets)

    pdf = FPDF()
    pdf.add_page()
    pdf.set_font("Arial", size=12)

    pdf.cell(200, 10, f"Chillamp Selector - Preset pour {preset['bassiste']}", ln=True)
    pdf.cell(200, 10, f"Score de fidélité : {preset['score_fidelite']}%", ln=True)
    pdf.multi_cell(0, 10, f"\n{preset['message']}\n")

    pdf.cell(200, 10, "Chaîne du signal :", ln=True)
    pdf.multi_cell(0, 10, f"{basse} → {', '.join(effets)} → {ampli} → {baffle}\n")

    pdf.cell(200, 10, "Réglages des effets :", ln=True)
    for effet, reglages in preset['reglages']['reglages_effets'].items():
        pdf.multi_cell(0, 10, f"{effet} : {reglages}")

    temp = tempfile.NamedTemporaryFile(delete=False, suffix=".pdf")
    pdf.output(temp.name)
    return send_file(temp.name, as_attachment=True, download_name="preset_chillamp.pdf")

if __name__ == '__main__':
    app.run(debug=True)

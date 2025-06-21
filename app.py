from flask import Flask, render_template, request, jsonify, send_file
from preset_engine import get_presets_for_combination
from presets import presets
from fpdf import FPDF
import io

# Initialisation de l'application Flask
app = Flask(__name__)

@app.route('/')
def index():
    """
    Page d'accueil : formulaire de sélection des paramètres.
    """
    return render_template('index.html')

@app.route('/bassistes')
def bassistes():
    """
    Renvoie la liste des bassistes disponibles en JSON.
    """
    noms = sorted(preset['nom'] for preset in presets)
    return jsonify(noms)

@app.route('/get_preset', methods=['POST'])
def get_preset():
    """
    Point de terminaison AJAX pour récupérer un preset selon la configuration choisie.
    """
    data = request.get_json() or {}
    resultat = get_presets_for_combination(
        data.get('bassiste'),
        data.get('basse'),
        data.get('ampli'),
        data.get('baffle'),
        data.get('effets', [])
    )
    return jsonify(resultat)

@app.route('/generate_pdf', methods=['POST'])
def generate_pdf():
    """
    Génère un PDF du preset et le renvoie en téléchargement.
    """
    try:
        # Récupération des données du formulaire
        data = request.form.to_dict(flat=False)
        bassiste = data.get('bassiste', [''])[0]
        basse     = data.get('basse', [''])[0]
        ampli     = data.get('ampli', [''])[0]
        baffle    = data.get('baffle', [''])[0]
        effets    = data.get('effets', [])

        # Calcul du preset
        preset = get_presets_for_combination(bassiste, basse, ampli, baffle, effets)

        # Création du PDF avec police Unicode
        pdf = FPDF()
        pdf.add_page()
        # Ajout des polices Unicode DejaVu (regular et bold)
        font_path = '/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf'
        pdf.add_font('DejaVu', '', font_path, uni=True)
        pdf.add_font('DejaVu', 'B', font_path, uni=True)
        pdf.set_font('DejaVu', '', 12)

        # Contenu du PDF
        pdf.cell(0, 10, f"Chillamp Selector - Preset pour {preset['bassiste']}", ln=True)
        pdf.set_font('DejaVu', 'B', 12)
        pdf.cell(0, 10, f"Score de fidélité : {preset['score_fidelite']} %", ln=True)
        pdf.ln(5)
        pdf.set_font('DejaVu', '', 12)
        pdf.multi_cell(0, 10, preset['message'])
        pdf.ln(10)

        # Chaîne du signal
        pdf.set_font('DejaVu', 'B', 12)
        pdf.cell(0, 10, 'Chaîne du signal :', ln=True)
        pdf.set_font('DejaVu', '', 12)
        chemin_signal = f"{basse} → {', '.join(effets)} → {ampli} → {baffle}"
        pdf.multi_cell(0, 10, chemin_signal)
        pdf.ln(5)

        # Réglages des effets
        pdf.set_font('DejaVu', 'B', 12)
        pdf.cell(0, 10, 'Réglages des effets :', ln=True)
        pdf.set_font('DejaVu', '', 12)
        for effet, reglages in preset['reglages']['reglages_effets'].items():
            pdf.multi_cell(0, 8, f"- {effet} : {reglages}")

        # Export en mémoire
        raw = pdf.output(dest='S')
        pdf_bytes = raw.encode('latin-1') if isinstance(raw, str) else raw
        buffer = io.BytesIO(pdf_bytes)
        buffer.seek(0)

        # Envoi du PDF
        return send_file(
            buffer,
            mimetype='application/pdf',
            as_attachment=True,
            download_name='preset_chillamp.pdf'
        )

    except Exception as e:
        # Journalisation de l'erreur pour debug
        app.logger.error('Erreur génération PDF : %s', e, exc_info=True)
        return (f"Erreur interne lors de la génération du PDF: {e}", 500)

if __name__ == '__main__':
    # Démarrage de l'application en mode debug pour dev local
    app.run(debug=True, host='0.0.0.0', port=5000)
```

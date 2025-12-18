from flask import Flask, render_template_string, send_from_directory
import sqlite3
import os

app = Flask(__name__)

# Configuration
DB_NAME = "securite.db"
IMAGE_FOLDER = "."

def init_db():
    """Crée la table si elle n'existe pas"""
    conn = sqlite3.connect(DB_NAME)
    # On stocke : ID, Date, Objets détectés, Nom du fichier image
    conn.execute('CREATE TABLE IF NOT EXISTS historique (id INTEGER PRIMARY KEY, date TEXT, objets TEXT, image TEXT)')
    conn.close()

@app.route('/')
def index():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    # Récupère les 50 derniers événements, du plus récent au plus ancien
    events = conn.execute('SELECT * FROM historique ORDER BY id DESC LIMIT 50').fetchall()
    conn.close()
    
    # Template HTML simple intégré
    html = """
    <!doctype html>
    <title>Journal de Surveillance</title>
    <style>
        body { font-family: sans-serif; padding: 20px; }
        .event { border: 1px solid #ddd; padding: 10px; margin-bottom: 10px; border-radius: 5px; }
        img { max-width: 300px; display: block; margin-top: 10px; }
        .alert { color: red; font-weight: bold; }
    </style>
    <h1>Historique des Détections</h1>
    {% for event in events %}
        <div class="event">
            <div><strong>Date :</strong> {{ event.date }}</div>
            <div class="alert">Objets : {{ event.objets }}</div>
            {% if event.image %}
                <img src="/images/{{ event.image }}" alt="Preuve">
            {% endif %}
        </div>
    {% endfor %}
    """
    return render_template_string(html, events=events)

# Route pour servir les images stockées localement
@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)

if __name__ == '__main__':
    init_db()
    # Lancement du serveur web sur le port 5000
    app.run(host='0.0.0.0', port=5001, debug=True)
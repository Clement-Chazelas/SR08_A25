from flask import Flask, render_template_string, send_from_directory
import sqlite3
import os
import sys

# Tente d'importer pyngrok pour l'automatisation du cloud
try:
    from pyngrok import ngrok
except ImportError:
    ngrok = None

app = Flask(__name__)

# Configuration
DB_NAME = "securite.db"
IMAGE_FOLDER = "."
PORT = 5001


def init_db():
    """Crée la table si elle n'existe pas"""
    conn = sqlite3.connect(DB_NAME)
    conn.execute('CREATE TABLE IF NOT EXISTS historique (id INTEGER PRIMARY KEY, date TEXT, objets TEXT, image TEXT)')
    conn.close()


@app.route('/')
def index():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    events = conn.execute('SELECT * FROM historique ORDER BY id DESC LIMIT 50').fetchall()
    conn.close()

    html = """
    <!doctype html>
    <title>Surveillance Cloud</title>
    <meta name="viewport" content="width=device-width, initial-scale=1">
    <style>
        body { font-family: sans-serif; padding: 20px; max-width: 800px; margin: auto; background-color: #f4f4f4; }
        h1 { text-align: center; color: #333; }
        .event { background: white; border: 1px solid #ddd; padding: 15px; margin-bottom: 15px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
        .meta { color: #666; font-size: 0.9em; margin-bottom: 5px; }
        .alert { color: #d9534f; font-weight: bold; font-size: 1.1em; }
        img { max-width: 100%; height: auto; display: block; margin-top: 10px; border-radius: 4px; }
        .footer { text-align: center; margin-top: 20px; font-size: 0.8em; color: #888; }
    </style>
    <h1>☁️ Journal de Surveillance</h1>
    {% for event in events %}
        <div class="event">
            <div class="meta"> {{ event.date }}</div>
            <div class="alert">️ Détection : {{ event.objets }}</div>
            {% if event.image %}
                <img src="/images/{{ event.image }}" alt="Preuve">
            {% endif %}
        </div>
    {% endfor %}
    <div class="footer">Système SR08 - Connecté au Cloud</div>
    """
    return render_template_string(html, events=events)


@app.route('/images/<path:filename>')
def serve_image(filename):
    return send_from_directory(IMAGE_FOLDER, filename)


if __name__ == '__main__':
    init_db()

    # --- AUTOMATISATION CLOUD (NGROK) ---
    if ngrok:
        # On ferme les anciens tunnels au cas où
        ngrok.kill()
        # On ouvre le tunnel sur le port 5001
        try:
            public_url = ngrok.connect(PORT).public_url
            print("\n" + "=" * 50)
            print(f" GLOBAL ACCESS (CLOUD) : {public_url}")
            print("=" * 50 + "\n")
        except Exception as e:
            print(f"Erreur démarrage Ngrok: {e}")
            print("Vérifiez que vous avez bien mis votre authtoken (ngrok config add-authtoken ...)")
    else:
        print("Note : Installez 'pyngrok' pour avoir le lien cloud automatique.")

    # Lancement du serveur
    app.run(host='0.0.0.0', port=PORT, debug=False)  # Debug False pour éviter le double lancement avec ngrok
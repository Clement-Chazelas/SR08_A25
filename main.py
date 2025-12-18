import cv2
from ultralytics import YOLO
from gpiozero import MotionSensor
from time import sleep
import datetime
import os
import sqlite3  # Ajout pour la base de données

# --- CONFIGURATION ---
PIN_PIR = 4            # Pin GPIO 4 (Broche physique 7)
MODEL_NAME = "yolov8n.pt" # Modèle Nano
CONFIDENCE_THRESHOLD = 0.4 # Seuil de confiance (40%)

# --- INITIALISATION ---
print("1. Chargement du modèle IA... (Cela peut prendre un moment)")
model = YOLO(MODEL_NAME)

print("2. Initialisation du capteur PIR sur GPIO", PIN_PIR)
pir = MotionSensor(PIN_PIR)

print("3. Connexion à la Webcam...")
camera = cv2.VideoCapture(0) # 0 = Première webcam USB connectée

# Vérification technique caméra
if not camera.isOpened():
    print("ERREUR CRITIQUE : Webcam non détectée.")
    print("Vérifiez le câble USB et redémarrez le script.")
    exit()
else:
    ret, frame = camera.read()
    if ret:
        print("   -> Webcam OK (Résolution: %dx%d)" % (frame.shape[1], frame.shape[0]))
    else:
        print("   -> Attention : Webcam détectée mais image noire.")

print("\n--- SYSTÈME PRÊT ET ARMÉ ---")
print("En attente de mouvement...")

try:
    while True:
        # La boucle s'arrête ici tant qu'il n'y a pas de mouvement
        pir.wait_for_motion()

        print("\n>>> MOUVEMENT DÉTECTÉ ! Analyse en cours...")

        # Capture de stabilisation
        for _ in range(5):
            ret, frame = camera.read()

        if not ret:
            print("Erreur lecture image.")
            continue

        # ANALYSE IA
        results = model(frame, verbose=False)
        detections = results[0]

        anomalie_confirmee = False
        objets_vus = []

        for box in detections.boxes:
            conf = float(box.conf)
            cls = int(box.cls)
            label = model.names[cls]

            if conf > CONFIDENCE_THRESHOLD:
                objets_vus.append(f"{label} ({int(conf*100)}%)")

                # CRITÈRE D'ALERTE : Personne détectée
                if label == 'person':
                    anomalie_confirmee = True

        if objets_vus:
            print(f"   Objets identifiés : {', '.join(objets_vus)}")
        else:
            print("   Rien d'identifiable.")

        if anomalie_confirmee:
            now = datetime.datetime.now()
            
            # Format pour le nom de fichier (sans espaces ni caractères spéciaux)
            timestamp_file = now.strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"ALERTE_{timestamp_file}.jpg"
            
            # Format pour l'affichage humain (Demandé)
            date_lisible = now.strftime("%d/%m/%Y à %H:%M:%S")

            # Sauvegarde image
            image_avec_cadres = results[0].plot()
            cv2.imwrite(filename, image_avec_cadres)
            print(f"   [ALARME] Intrusion confirmée ! Preuve : {filename}")

            # --- ENREGISTREMENT BDD ---
            try:
                conn = sqlite3.connect("securite.db")
                cursor = conn.cursor()
                
                liste_objets_str = ", ".join(objets_vus)
                
                # On insère la date lisible au lieu du timestamp brut
                cursor.execute("INSERT INTO historique (date, objets, image) VALUES (?, ?, ?)", 
                               (date_lisible, liste_objets_str, filename))
                
                conn.commit()
                conn.close()
                print("   -> Enregistré en BDD.")
            except Exception as e:
                print(f"   Erreur BDD: {e}")

        # Temporisation
        print("... Temporisation 5 sec ...")
        sleep(5)

        print("Système réarmé. En attente.")
        pir.wait_for_no_motion()

except KeyboardInterrupt:
    print("\nArrêt du système demandé par l'utilisateur.")
    camera.release()
    print("Caméra libérée. Au revoir.")
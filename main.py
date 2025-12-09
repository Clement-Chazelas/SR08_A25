import cv2
from ultralytics import YOLO
from gpiozero import MotionSensor
from time import sleep
import datetime
import os

# --- CONFIGURATION ---
PIN_PIR = 4            # Pin GPIO 4 (Broche physique 7)
MODEL_NAME = "yolov8n.pt" # Modèle Nano (recommandé pour la vitesse)
CONFIDENCE_THRESHOLD = 0.4 # Seuil de confiance (40%)

# --- INITIALISATION ---
print("1. Chargement du modèle IA... (Cela peut prendre un moment)")
model = YOLO(MODEL_NAME) # Téléchargera yolov8n.pt automatiquement au 1er lancement

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
    # On lit une image à vide pour "chauffer" la caméra
    ret, frame = camera.read()
    if ret:
        print("   -> Webcam OK (Résolution: %dx%d)" % (frame.shape[1], frame.shape[0]))
    else:
        print("   -> Attention : Webcam détectée mais image noire.")

print("\n--- SYSTÈME PRÊT ET ARMÉ ---")
print("En attente de mouvement...")

try:
    while True:
        # La boucle s'arrête ici tant qu'il n'y a pas de mouvement (Economie CPU)
        pir.wait_for_motion()

        print("\n>>> MOUVEMENT DÉTECTÉ ! Analyse en cours...")

        # On capture plusieurs frames pour laisser le temps à l'autofocus/lumière
        for _ in range(5):
            ret, frame = camera.read()

        if not ret:
            print("Erreur lecture image.")
            continue

        # ANALYSE IA (Inférence)
        # verbose=False évite de polluer le terminal avec trop de texte
        results = model(frame, verbose=False)
        detections = results[0] # Premier résultat (une seule image)

        anomalie_confirmee = False
        objets_vus = []

        # On regarde ce que l'IA a trouvé
        for box in detections.boxes:
            conf = float(box.conf)
            cls = int(box.cls)
            label = model.names[cls]

            # On ne garde que ce qui est sûr à > 40%
            if conf > CONFIDENCE_THRESHOLD:
                objets_vus.append(f"{label} ({int(conf*100)}%)")

                # CRITÈRE D'ALERTE : Si on voit une personne
                # (Vous pourrez ajouter 'backpack' ou 'handbag' ici plus tard)
                if label == 'person':
                    anomalie_confirmee = True

        if objets_vus:
            print(f"   Objets identifiés : {', '.join(objets_vus)}")
        else:
            print("   Rien d'identifiable.")

        # SI C'EST UNE ANOMALIE
        if anomalie_confirmee:
            # Génération du nom de fichier unique
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
            filename = f"ALERTE_{timestamp}.jpg"

            # L'IA dessine les rectangles sur l'image pour nous
            image_avec_cadres = results[0].plot()

            # Sauvegarde sur la carte SD
            cv2.imwrite(filename, image_avec_cadres)
            print(f"   [ALARME] Intrusion confirmée ! Preuve sauvegardée : {filename}")

            # --- C'est ici qu'on insérera l'envoi vers le Cloud plus tard ---

        # Pause pour éviter de mitrailler (le PIR reste actif quelques secondes)
        print("... Temporisation 5 sec ...")
        sleep(5)

        print("Système réarmé. En attente.")
        pir.wait_for_no_motion()

except KeyboardInterrupt:
    print("\nArrêt du système demandé par l'utilisateur.")
    camera.release()
    print("Caméra libérée. Au revoir.")

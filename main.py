import cv2
from ultralytics import YOLO
from gpiozero import MotionSensor
from time import sleep
import datetime
import os
import sqlite3

# --- CONFIGURATION ---
PIN_PIR = 4
MODEL_NAME = "yolov8n.pt"
CONFIDENCE_THRESHOLD = 0.4
DB_FILE = "securite.db"

# --- INITIALISATION ---
print("--- DÉMARRAGE SYSTÈME SR08 ---")
print("1. Chargement IA...")
model = YOLO(MODEL_NAME)

print(f"2. Capteur PIR (GPIO {PIN_PIR})...")
pir = MotionSensor(PIN_PIR)

print("3. Webcam...")
camera = cv2.VideoCapture(0)

if not camera.isOpened():
    print("ERREUR : Webcam absente.")
    exit()
else:
    ret, frame = camera.read()
    if ret:
        print(f"   -> Webcam OK ({frame.shape[1]}x{frame.shape[0]})")

print("\n>>> SYSTÈME EN LIGNE ET CONNECTÉ À LA BASE DE DONNÉES <<<")
print("Les alertes seront visibles sur l'interface Web (Locale & Cloud).")

try:
    while True:
        pir.wait_for_motion()
        print("\n[MOUVEMENT] Analyse...")

        # Stabilisation image
        for _ in range(5):
            ret, frame = camera.read()

        if not ret: continue

        # IA
        results = model(frame, verbose=False)
        detections = results[0]

        personne_detectee = False
        labels_trouves = []

        for box in detections.boxes:
            conf = float(box.conf)
            cls = int(box.cls)
            label = model.names[cls]

            if conf > CONFIDENCE_THRESHOLD:
                labels_trouves.append(f"{label} {int(conf * 100)}%")
                if label == 'person':
                    personne_detectee = True

        if labels_trouves:
            print(f"   Vu : {', '.join(labels_trouves)}")

        if personne_detectee:
            now = datetime.datetime.now()
            filename = f"ALERTE_{now.strftime('%Y-%m-%d_%H-%M-%S')}.jpg"
            date_lisible = now.strftime("%d/%m/%Y à %H:%M:%S")

            # Sauvegarde Image
            image_annotee = results[0].plot()
            cv2.imwrite(filename, image_annotee)

            # Sauvegarde Base de Données
            try:
                conn = sqlite3.connect(DB_FILE)
                cursor = conn.cursor()
                cursor.execute("INSERT INTO historique (date, objets, image) VALUES (?, ?, ?)",
                               (date_lisible, ", ".join(labels_trouves), filename))
                conn.commit()
                conn.close()
                print(f"   [ALERTE] Sauvegardée et synchronisée Cloud (Fichier: {filename})")
            except Exception as e:
                print(f"   Erreur BDD: {e}")

        sleep(5)
        pir.wait_for_no_motion()

except KeyboardInterrupt:
    camera.release()
    print("\nArrêt.")
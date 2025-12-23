# Système de Surveillance Intelligent (SR08)

Ce projet est une solution de sécurité IoT autonome. Il combine la détection physique (capteur PIR) pour l'économie d'énergie et l'intelligence artificielle (YOLOv8) pour la validation visuelle des intrusions. Les alertes sont stockées localement et accessibles via une interface web, consultable en local ou via le Cloud.

## Stack Technique

* **Langage** : Python 3.x
* **Vision par Ordinateur** : OpenCV (`opencv-python`)
* **IA** : Ultralytics YOLOv8 (Modèle Nano `yolov8n.pt`)
* **Interface Web** : Flask
* **Base de Données** : SQLite (Intégrée)
* **Matériel (IoT)** : Gpiozero (Gestion du PIR)
* **Cloud / Accès Distant** : Ngrok (Tunneling)

## Prérequis Matériel

1.  **Raspberry Pi** (ou PC pour test).
2.  **Webcam USB**.
3.  **Capteur de mouvement PIR** (Pin DATA sur GPIO 4 / Broche 7).

## Installation

1.  **Fichiers** : Placez `main.py` et `interface.py` dans le même dossier.
2.  **Dépendances** :
    ```bash
    pip install flask opencv-python ultralytics gpiozero
    ```
3.  **Outil Cloud (Ngrok)** :
    * Installez Ngrok : `sudo apt install ngrok` (sur Raspberry Pi) ou via le site officiel.
    * Connectez votre compte (obligatoire pour le cloud) :
      ```bash
      ngrok config add-authtoken VOTRE_TOKEN
      ```

## Démarrage du Système (3 Terminaux)

Pour avoir le système complet (Détection + Site Web + Accès Cloud), lancez ces 3 commandes dans des terminaux séparés.

### 1. Lancer l'Interface Web
```bash
python interface.py
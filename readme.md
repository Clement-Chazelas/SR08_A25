# Système de Surveillance Intelligent (SR08)

Ce projet est une solution de sécurité IoT autonome. Il combine la détection physique (capteur PIR) pour l'économie d'énergie et l'intelligence artificielle (YOLOv8) pour la validation visuelle des intrusions. Les alertes sont archivées dans une base de données locale et accessibles via une interface web dédiée.

## Stack Technique

* **Langage** : Python 3.13
* **Vision par Ordinateur** : OpenCV (`opencv-python`)
* **Intelligence Artificielle** : Ultralytics YOLOv8 (Modèle Nano `yolov8n.pt`)
* **Interface Web** : Flask
* **Base de Données** : SQLite (Intégrée, aucun serveur requis)
* **Matériel (IoT)** : Gpiozero (Gestion des interruptions matérielles)
* **Accès Distant** : Ngrok (Tunneling sécurisé)

## Prérequis Matériel

1.  **Raspberry Pi** 
2.  **Webcam USB** générique.
3.  **Capteur de mouvement PIR**.
    * *Branchement* : a compléter

## Installation

1.  **Préparation des fichiers**
    Placez `main.py` et `interface.py` dans le même dossier.

2.  **Installation des dépendances**
    Exécutez la commande suivante pour installer les bibliothèques nécessaires :

```bash
pip install flask opencv-python ultralytics gpiozero

## Ordre de lancement des commandes
python interface.py
python main.py
ngrok http 5001 (Pour consulter la caméra depuis l'extérieur du réseau local (4G, autre wifi).

## Fonctionnement détaillé

Fonctionnement Technique Détaillé
Le système fonctionne selon une boucle logique optimisée pour réduire la consommation CPU et éviter les faux positifs.

1. Module de Détection (main.py)
Ce script agit comme le "cerveau" du dispositif.

État de Veille (Low Power) : Le système utilise pir.wait_for_motion(). À ce stade, le processeur est au repos et la caméra ne capture pas d'images. Seul le capteur physique est écouté.

Réveil et Capture : Lorsqu'un mouvement physique est détecté par le PIR, le script active la webcam. Il capture une rafale de 5 images pour laisser le temps à l'autofocus et à l'exposition automatique de la caméra de se stabiliser.

Inférence IA (YOLOv8) : La dernière image est envoyée au réseau de neurones. YOLO analyse l'image pour identifier des objets (personnes, animaux, véhicules).

Filtrage Logique : Une alerte n'est déclenchée que si deux conditions sont réunies :

L'objet détecté est de type person (configurable).

Le taux de confiance (probabilité) est supérieur à 40%.

Enregistrement : Si l'alerte est validée :

L'image est annotée (rectangles de détection) et sauvegardée en .jpg.

Une entrée est créée dans la base de données securite.db avec l'horodatage, le type d'objet et le lien vers l'image.

2. Module Web et Données (interface.py)
Ce script assure l'interface Homme-Machine (IHM).

Serveur Flask : Il écoute sur le port 5001.

Base de Données SQLite : À chaque actualisation de la page, le script interroge la table historique du fichier securite.db. Il récupère les 50 derniers événements triés du plus récent au plus ancien.

Affichage Dynamique : Le template HTML est généré à la volée pour afficher la liste des intrusions avec la date précise et la photo de preuve correspondante.
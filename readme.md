# Système de Surveillance Intelligent (SR08)

Ce projet est une solution de sécurité **IoT (Internet of Things)** autonome, conçue pour la surveillance de zones sensibles (type musée).

L'architecture privilégie une approche **"Green IT"** et **Edge Computing** : le système reste en veille pour économiser l'énergie et ne déclenche l'analyse lourde (Intelligence Artificielle) que lorsqu'une présence physique est détectée. Les alertes sont consultables en temps réel via une interface Web locale synchronisée avec le Cloud.

---

## 🛠️ Stack Technique

Le projet s'appuie sur une stack Python moderne et optimisée pour l'embarqué :

* **Matériel (Edge)** :
    * **Raspberry Pi 4** (OS 64-bit).
    * **Capteur PIR** : Déclencheur physique basse consommation.
    * **Webcam** : Acquisition vidéo à la demande.
* **Intelligence Artificielle & Vision** :
    * **YOLOv8 Nano (Ultralytics)** : Modèle de détection d'objets rapide et léger, capable d'identifier une personne en moins de 200ms sur RPi.
    * **OpenCV** : Traitement des flux vidéo et capture des preuves.
* **Backend & Données** :
    * **Flask** : Serveur Web léger pour l'interface de gestion.
    * **SQLite** : Base de données embarquée pour l'historique des événements (Date, Objet, Photo).
* **Infrastructure & Cloud** :
    * **Pyngrok** : Automatisation du tunneling sécurisé pour rendre le Raspberry Pi accessible depuis internet sans configuration de routeur.

---

## 🔌 Câblage Matériel

Pour que le script fonctionne, le montage suivant est requis :

* **Webcam** : Port USB 3.0 (Bleu).
* **Capteur PIR** :
    * VCC → Pin 2 (5V)
    * GND → Pin 6 (GND)
    * **OUT (Data) → Pin 7 (GPIO 4)**

---

## 🚀 Installation

### 1. Prérequis
Assurez-vous d'utiliser **Raspberry Pi OS (64-bit)** pour la compatibilité avec les bibliothèques d'IA modernes (Torch/YOLO).

### 2. Récupération du projet
Ouvrez un terminal sur le Raspberry Pi :
```bash
cd ~
git clone [https://github.com/Clement-Chazelas/SR08_A25.git](https://github.com/Clement-Chazelas/SR08_A25.git)
cd SR08_A25

# 🏥 MediERP Professional

**Système ERP Médical Avancé avec IA Prédictive et Authentification Biométrique**

> Une solution Desktop complète pour la gestion médicale moderne, optimisée pour la performance et l'expérience utilisateur avec un design "Full Light" professionnel développé en Python/PySide6.

---

## ✨ Points Forts
- 🎨 **Design Premium** — Interface "Full Light" épurée, moderne et intuitive (PySide6).
- 🛡️ **Système RBAC "Antigravity"** — 5 rôles distincts avec espaces dédiés : Administrateur, Médecin, Secrétaire, Assistant, et Patient.
- 🔄 **Workflow Connecté** — Flux complet : Arrivée ➡️ Prise de constantes (Assistant) ➡️ Consultation IA (Médecin) ➡️ Facturation (Secrétaire).
- 🤖 **IA Prédictive** — Analyse des risques cardiaques via Machine Learning (Scikit-learn) intégrée à la consultation.
- 🔐 **Sécurité Multi-Facteurs** — Authentification par mot de passe robuste, avec reconnaissance faciale et vocale.
- 📊 **Gestion des Stocks** — Suivi de l'inventaire médical (vaccins, matériel) avec alertes de seuil par l'Assistant.
- 📱 **Portail Patient** — Espace en ligne simulé pour suivre ses rendez-vous, ordonnances et constantes.

---

## 🏗️ Architecture du Système

MediERP est une application Desktop robuste construite sur une architecture modulaire en Python.

### 🔹 Composants Principaux
*   **Core**: Gestion du cycle de vie de l'application, sécurité et événements (`src/core`).
*   **UI Desktop**: Interface riche développée en PySide6 avec styles QSS personnalisés (`src/views`).
*   **Intelligence Artificielle**: Modèles ML pour le diagnostic et services biométriques (`src/services`).
*   **Persistance**: SQLite avec chiffrement pour la confidentialité absolue des données médicales.

---

## 📂 Structure du Projet

```text
MediERP/
├── src/
│   ├── core/           # Moteur de l'application (Database, Security, Events)
│   ├── views/          # Interface Desktop PyQt6/PySide6 (.py & .ui)
│   ├── services/       # Services IA (Face Recog, ML, Voice, Speech)
│   ├── models/         # Modèles de données (Patient, User, Base)
│   └── utils/          # Utilitaires et compatibilité Qt
├── database/           # Schémas SQL et scripts de migration
├── db/                 # Bases de données SQLite locales
├── config/             # Paramètres système et feuilles de style QSS
├── assets/             # Modèles ML (.pkl), Fonts, et Multimédia
├── tests/              # Suite de tests unitaires et d'intégration
└── main.py             # Point d'entrée de l'application
```

---

## 🚀 Installation et Lancement

1.  **Prérequis**: Python 3.10+
2.  **Environnement**:
    ```bash
    python -m venv venv
    venv\Scripts\activate
    pip install -r requirements.txt
    ```
3.  **Lancement**:
    ```bash
    python main.py
    ```

---

## 📋 Stack Technique

| Domaine | Technologies |
| :--- | :--- |
| **Langage** | Python 3.12 |
| **GUI Framework** | PySide6 / PyQt6 |
| **Base de Données** | SQLite3 |
| **Machine Learning** | Scikit-learn, OpenCV, NumPy |
| **Sécurité** | Biométrie, Bcrypt, Cryptography |
| **Services** | Dictée vocale, Génération PDF (ReportLab) |

---

## 📄 Licence
Propriété de **Benzarti Ahmed Yassine**. Tous droits réservés.

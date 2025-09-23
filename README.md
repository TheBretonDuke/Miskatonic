# 🧙‍♂️ Miskatonic Quiz

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/MongoDB-Questions-47A248?logo=mongodb&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLite-Users-003B57?logo=sqlite&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-Required-2496ED?logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-yellow" />
</p>

---

Générateur de **quiz** avec **FastAPI**, **MongoDB** et **SQLite**.  
Ambiance inspirée de la **Miskatonic University** et du **Seigneur des Anneaux**.  

---

## 📖 Sommaire
- [✨ Fonctionnalités](#-fonctionnalités)
- [🛠️ Stack technique](#%EF%B8%8F-stack-technique)
- [📂 Arborescence](#-arborescence)
- [⚙️ Installation](#%EF%B8%8F-installation)
- [📊 Données & ETL](#-données--etl)
- [🚀 Lancement](#-lancement)
- [🔌 API (endpoints)](#-api-endpoints)
- [🎨 Frontend](#-frontend)
- [👥 Utilisateurs & rôles](#-utilisateurs--rôles)
- [🛠️ Dépannage rapide](#%EF%B8%8F-dépannage-rapide)
- [📸 Aperçu visuel](#-aperçu-visuel)
- [🤝 Contribuer](#-contribuer)
- [📜 Licence & auteurs](#-licence--auteurs)

---

## ✨ Fonctionnalités
- Quiz thématiques : importés depuis **CSV → MongoDB** via un pipeline ETL  
- Authentification utilisateurs (SQLite) avec rôles : `prof`, `eleve`, `admin`  
- API REST (FastAPI) : `/register`, `/login`, `/questions`, `/answer`  
- Frontend en **HTML/CSS** (Bootstrap + thème médiéval custom)  
- Base **MongoDB en Docker** (zéro config locale)  
- Hot-reload backend avec **Uvicorn**  

---

## 🛠️ Stack technique
- **Backend** : FastAPI, Uvicorn  
- **Bases de données** : MongoDB (questions), SQLite (utilisateurs & rôles)  
- **Frontend** : HTML, CSS (Bootstrap + thème custom)  
- **ETL** : pandas, pymongo  
- **Conteneurisation** : Docker (MongoDB)  

---

## 📂 Arborescence
```bash
Miskatonic-Quiz/
├─ app/
│  ├─ main.py
│  ├─ routers/
│  ├─ models/
│  └─ services/
├─ data/
│  └─ users.db   # SQLite (créé au premier lancement si absent)
├─ etl/
│  ├─ questions.csv
│  └─ etl_questions.py
├─ frontend/
│  ├─ index.html
│  ├─ questions.html
│  └─ quiz.html
├─ requirements.txt
└─ README.md
```

---

## ⚙️ Installation

```bash
# Cloner le repo
git clone https://github.com/TheBretonDuke/Miskatonic.git
cd Miskatonic

# Créer un environnement virtuel
python -m venv .venvquiz

# Activer l'environnement
# macOS / Linux
source .venvquiz/bin/activate
# Windows (PowerShell)
.venvquiz\Scripts\Activate.ps1

# Installer les dépendances
pip install -r requirements.txt
```

---

## 📊 Données & ETL

Importer les questions CSV dans MongoDB :

```bash
python etl/etl_questions.py
```

Sortie attendue :
```
Base Mongo prête : 76 questions insérées.
```

Paramètres de connexion MongoDB :  
- URI : `mongodb://localhost:27017`  
- Base : `miskatonic_quiz`  
- Collection : `questions`  

---

## 🚀 Lancement

Démarrer le backend en hot-reload :

```bash
uvicorn app.main:app --reload
```

Accès :  
- API : [http://127.0.0.1:8000](http://127.0.0.1:8000)  
- Swagger UI : [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  

---

## 🔌 API (endpoints)

### Authentification
```http
POST /register
{
  "username": "simon",
  "password": "monmotdepasse",
  "role": "eleve"
}

POST /login
{
  "username": "simon",
  "password": "monmotdepasse"
}
```

### Questions
```http
GET /questions?theme=magie&difficulte=facile&page=1
```

### Réponses
```http
POST /answer
{
  "question_id": "654321abcdef",
  "selected_option": "B"
}
```

---

## 🎨 Frontend
- `frontend/index.html` → Connexion / Inscription  
- `frontend/questions.html` → Liste des questions  
- `frontend/quiz.html` → Lancer le quiz  

---

## 👥 Utilisateurs & rôles
- **prof** — gestion avancée (création thèmes, suivi élèves)  
- **eleve** — jeu et progression  
- **admin** — supervision globale  

Stockage : `data/users.db` (SQLite)  

---

## 🛠️ Dépannage rapide
- **MongoDB non démarré** → `docker start mongodb_quiz`  
- **Aucune question trouvée** → `python etl/etl_questions.py`  
- **SQLite introuvable** → créé automatiquement au premier `POST /register`  

---

## 📸 Aperçu visuel
*(screenshots à ajouter ici, ex. page de connexion, quiz en cours…)*  

---

## 🤝 Contribuer
1. Fork le repo  
2. Crée une branche : `git checkout -b feature/nouvelle-fonctionnalité`  
3. Commit : `git commit -m "Ajout nouvelle fonctionnalité"`  
4. Push : `git push origin feature/nouvelle-fonctionnalité`  
5. Ouvre une Pull Request 🚀  

---

## 📜 Licence & auteurs
- Licence : [MIT](LICENSE)  

### Auteurs
- [Lucie Jouan](https://github.com/luciej0507)  
- [Simon Brouard](https://github.com/TheBretonDuke)  

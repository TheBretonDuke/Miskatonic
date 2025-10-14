# Miskatonic Quiz

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.11%2B-3776AB?logo=python&logoColor=white" />
  <img src="https://img.shields.io/badge/FastAPI-Backend-009688?logo=fastapi&logoColor=white" />
  <img src="https://img.shields.io/badge/MongoDB-Questions-47A248?logo=mongodb&logoColor=white" />
  <img src="https://img.shields.io/badge/SQLite-Users-003B57?logo=sqlite&logoColor=white" />
  <img src="https://img.shields.io/badge/Docker-Required-2496ED?logo=docker&logoColor=white" />
  <img src="https://img.shields.io/badge/License-MIT-yellow" />
</p>


<p align="center">
  <img src="https://img.shields.io/badge/Architecture-Modular-success" />
  <img src="https://img.shields.io/badge/Main.py-25%20lines-brightgreen" />
  <img src="https://img.shields.io/badge/Refactored-95%25%20reduction-orange" />
  <img src="https://img.shields.io/badge/Hot--reload-Enabled-blue" />
</p>

---

Générateur de **quiz** avec **FastAPI**, **MongoDB** et **SQLite**.  

---

## Sommaire
- [Architecture](#architecture)
- [Fonctionnalités](#fonctionnalités)
- [Stack technique](#stack-technique)
- [Arborescence](#arborescence)
- [Installation](#installation)
- [Données & ETL](#données--etl)
- [Lancement](#lancement)
- [API (endpoints)](#api-endpoints)
- [Frontend](#frontend)
- [Utilisateurs & rôles](#utilisateurs--rôles)
- [Dépannage rapide](#dépannage-rapide)
- [Aperçu visuel](#aperçu-visuel)
- [Contribuer](#contribuer)
- [Licence & auteurs](#licence--auteurs)

---

### ![Separation](https://img.shields.io/badge/Separation-Responsibilities-informational) Séparation des responsabilités
- **`main.py`** : Point d'entrée et configuration de l'app
- **`config.py`** : Métadonnées FastAPI et paramètres CORS
- **`models.py`** : Modèles Pydantic pour la validation
- **`utils.py`** : Fonctions utilitaires partagées
- **`routes/`** : Endpoints organisés par domaine métier
- **`database.py`** : Logique d'accès aux données SQLite
- **`questions.py`** : Logique d'accès aux données MongoDB

---

## ![Features](https://img.shields.io/badge/Features-Overview-brightgreen) Fonctionnalités

- ![Quiz](https://img.shields.io/badge/Quiz-Thematic-blue) **Quiz thématiques** : Questions importées depuis **CSV → MongoDB** via pipeline ETL  
- ![Auth](https://img.shields.io/badge/Auth-Secure-red) **Authentification** : Utilisateurs (SQLite) avec rôles : `etudiant`, `prof`, `admin`  
- ![API](https://img.shields.io/badge/API-REST-green) **API REST** : Endpoints organisés par domaine (`/auth`, `/questions`, `/quiz`, `/utils`)
- ![Frontend](https://img.shields.io/badge/Frontend-Themed-purple) **Frontend thématique** : HTML/CSS (Bootstrap + thème médiéval custom)  
- ![Docker](https://img.shields.io/badge/MongoDB-Containerized-blue) **MongoDB** : Zero config avec Docker
- ![HotReload](https://img.shields.io/badge/Hot--reload-Development-orange) **Hot-reload** : Développement avec Uvicorn --reload  

---

## ![Stack](https://img.shields.io/badge/Stack-Technical-informational) Stack technique
- **Backend** : FastAPI, Uvicorn  
- **Bases de données** : MongoDB (questions), SQLite (utilisateurs & rôles)  
- **Frontend** : HTML, CSS (Bootstrap + thème custom)  
- **ETL** : pandas, pymongo  
- **Conteneurisation** : Docker (MongoDB)  

---

## ![Structure](https://img.shields.io/badge/Project-Structure-yellow) Arborescence
```bash
Miskatonic/
├── app/                          # API Backend (Architecture modulaire)
│   ├── main.py                   # Point d'entrée (25 lignes)
│   ├── config.py                 # Configuration FastAPI & CORS
│   ├── models.py                 # Modèles Pydantic
│   ├── utils.py                  # Fonctions utilitaires
│   ├── database.py               # Logique SQLite (utilisateurs)
│   ├── questions.py              # Logique MongoDB (questions)
│   └── routes/                   # Routes organisées par domaine
│       ├── auth_routes.py        # Authentification (/login, /register)
│       ├── questions_routes.py   # Questions CRUD (/questions)
│       ├── quiz_routes.py        # Sessions quiz (/quiz/*)
│       └── utilities_routes.py   # Utilitaires (/themes, /tests, /answer)
├── data/                         # Stockage local
│   ├── users.db                  # SQLite (auto-créé)
│   ├── questions.csv             # Source des questions
│   └── mongodb/                  # Données MongoDB (Docker volume)
├── frontend/                     # Interface utilisateur
│   ├── index.html                # Page d'accueil/connexion
│   ├── questions.html            # Gestion questions (profs)
│   ├── quiz.html                 # Interface de quiz
│   └── style.css                 # Thème médiéval
├── etl.py                        # Pipeline CSV → MongoDB
├── requirements.txt              # Dépendances Python
├── docker-compose.yml            # Configuration Docker
└── README.md                     # Documentation
```

---

## ![Installation](https://img.shields.io/badge/Setup-Installation-blue) Installation

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

# Démarrer MongoDB (Docker)
docker run -d \
  --name mongodb_quiz \
  -p 27017:27017 \
  -v ~/data/mongodb:/data/db \
  mongo:7
```

---

## ![Data](https://img.shields.io/badge/Data-ETL-orange) Données & ETL

Importer les questions CSV dans MongoDB :

```bash
python etl.py
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

## ![Launch](https://img.shields.io/badge/Server-Launch-success) Lancement

Démarrer le backend en hot-reload :

```bash
uvicorn app.main:app --reload
```

Accès :  
- API : [http://127.0.0.1:8000](http://127.0.0.1:8000)  
- Swagger UI : [http://127.0.0.1:8000/docs](http://127.0.0.1:8000/docs)  

---

## ![API](https://img.shields.io/badge/API-Endpoints-green) API (endpoints)

### ![Auth](https://img.shields.io/badge/Auth-Security-red) Authentification
```http
POST /register                    # Créer un compte
{
  "username": "bob",
  "password": "monmotdepasse", 
  "role": "etudiant"             # etudiant | prof | admin
}

POST /login                      # Se connecter
{
  "username": "bob",
  "password": "monmotdepasse"
}
```

### ![Users](https://img.shields.io/badge/Users-Management-orange) Gestion des utilisateurs
```http
GET /users?admin_username=admin  # Lister tous les utilisateurs (admin)
GET /users/{username}?requesting_user=admin  # Info utilisateur

DELETE /users/{username}?admin_username=admin  # Supprimer (admin)
PUT /users/{username}/role       # Modifier rôle (admin)
{
  "admin_username": "admin",
  "target_username": "prof1", 
  "new_role": "admin"
}

PUT /users/{username}/password   # Changer son mot de passe
{
  "username": "prof1",
  "current_password": "ancien_mdp",
  "new_password": "nouveau_mdp"
}
```

### ![Questions](https://img.shields.io/badge/Questions-CRUD-blue) Questions (CRUD)
```http
GET /questions                   # Mode normal (échantillon aléatoire)
GET /questions?limit=10&theme=Maths
GET /questions?admin=true&username=prof1  # Mode admin (toutes)

POST /questions                  # Ajouter question (prof+)
{
  "username": "prof1",
  "question": "Combien font 2+2 ?",
  "theme": "Mathématiques",
  "test": "Calcul mental", 
  "choix": ["3", "4", "5", "6"],
  "correct": ["4"]
}

DELETE /questions?username=prof1&question=...  # Supprimer
```

### ![Quiz](https://img.shields.io/badge/Quiz-Sessions-purple) Quiz (Sessions)
```http
POST /quiz/create                # Créer session (prof+)
{
  "username": "prof1",
  "limit": 10,
  "name": "Quiz révision",
  "theme": "Mathématiques"
}

GET /quiz/{quiz_id}              # Récupérer session
DELETE /quiz/{quiz_id}?username=prof1  # Supprimer session
GET /quiz?username=prof1         # Lister ses quiz
```

### ![Utils](https://img.shields.io/badge/Utils-Helpers-yellow) Utilitaires
```http
GET /themes                      # Liste des thèmes
GET /tests                       # Liste des tests  
GET /themes_by_test/{test}       # Thèmes d'un test
GET /tests_by_theme/{theme}      # Tests d'un thème

POST /answer                     # Vérifier réponse
{
  "username": "etudiant1",
  "question": "Combien font 2+2 ?",
  "reponse": ["4"]
}
```

---

## ![Frontend](https://img.shields.io/badge/Frontend-Interface-pink) Frontend
- `frontend/index.html` → Connexion / Inscription  
- `frontend/questions.html` → Liste des questions  
- `frontend/quiz.html` → Lancer le quiz  

---

## ![Users](https://img.shields.io/badge/Users-Roles-lightblue) Utilisateurs & rôles
- ![Student](https://img.shields.io/badge/Role-Student-blue) **etudiant** — Passer des quiz uniquement  
- ![Teacher](https://img.shields.io/badge/Role-Teacher-green) **prof** — Créer/gérer questions et quiz, passer des quiz
- ![Admin](https://img.shields.io/badge/Role-Admin-red) **admin** — Accès complet système (supervision globale)

Stockage : `data/users.db` (SQLite, auto-créé au premier `/register`)

---

## ![Troubleshooting](https://img.shields.io/badge/Help-Troubleshooting-orange) Dépannage rapide
- **MongoDB non démarré** → `docker start mongodb_quiz`  
- **Aucune question trouvée** → `python etl.py`  
- **SQLite introuvable** → Créé automatiquement au premier `POST /register`
- **Port 8000 occupé** → `lsof -i :8000` puis `kill -9 <PID>`
- **Erreurs d'imports** → Réactiver l'environnement : `source .venvquiz/bin/activate`

---

## ![Preview](https://img.shields.io/badge/Preview-Visual-lightgrey) Aperçu visuel
*(screenshots à ajouter ici, ex. page de connexion, quiz en cours…)*  

---

## ![Contributing](https://img.shields.io/badge/Community-Contributing-brightgreen) Contribuer
1. Fork le repo  
2. Crée une branche : `git checkout -b feature/nouvelle-fonctionnalité`  
3. Commit : `git commit -m "Ajout nouvelle fonctionnalité"`  
4. Push : `git push origin feature/nouvelle-fonctionnalité`  
5. Ouvre une Pull Request  

---

## ![License](https://img.shields.io/badge/License-MIT-yellow) Licence & auteurs
- Licence : [MIT](LICENSE)
- Background GIF chargé depuis Giphy uniquement pour démonstration pédagogique.

### ![Authors](https://img.shields.io/badge/Team-Authors-blue) Auteurs
- [Lucie Jouan](https://github.com/luciej0507)  
- [Simon Brouard](https://github.com/TheBretonDuke)  

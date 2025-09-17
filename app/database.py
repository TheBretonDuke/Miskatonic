# ============================================================
# database.py
#
# Ce fichier centralise toutes les connexions aux bases de données :
#   - SQLite : pour gérer les utilisateurs (authentification, rôles)
#   - MongoDB : pour gérer les questions du quiz
#
# FastAPI utilisera ce fichier pour accéder aux deux bases.
# ============================================================

# =============================
# --- Partie 1 : SQLite (SQL) ---
# =============================

from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker

# URL de connexion vers SQLite
# -----------------------------
# "./data/users.db" = fichier de base de données SQLite
# "sqlite:///" = préfixe de connexion pour SQLite
SQLALCHEMY_DATABASE_URL = "sqlite:///./data/users.db"

# Création du moteur SQLAlchemy
# -----------------------------
# - connect_args={"check_same_thread": False} est nécessaire pour SQLite
#   car par défaut SQLite n'autorise pas l'accès multi-thread
engine = create_engine(
    SQLALCHEMY_DATABASE_URL,
    connect_args={"check_same_thread": False}
)

# Création d'une "Session" pour interagir avec la base
# ----------------------------------------------------
# - autocommit=False → il faut valider les transactions avec commit()
# - autoflush=False → évite que les requêtes partent trop tôt
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base de référence pour déclarer les modèles SQLAlchemy
# ------------------------------------------------------
# Exemple : un modèle User héritera de Base
Base = declarative_base()


# =============================
# --- Partie 2 : MongoDB (NoSQL) ---
# =============================

from pymongo import MongoClient

# Connexion au serveur MongoDB local
# ----------------------------------
# "mongodb://localhost:27017/" = URL par défaut
mongo_client = MongoClient("mongodb://localhost:27017/")

# Sélection de la base MongoDB
# ----------------------------
# Elle sera créée automatiquement si elle n'existe pas encore
mongo_db = mongo_client.quizdb

# Sélection de la collection "questions"
# --------------------------------------
# Comme une "table" en SQL, mais flexible
questions_collection = mongo_db.questions


# =============================
# --- Partie 3 : Dépendance FastAPI ---
# =============================

# Cette fonction permet à FastAPI de récupérer une session SQLite
# Elle sera utilisée avec "Depends" dans les routes
# Exemple :
#   def ma_route(db: Session = Depends(get_db)):
#       ...
def get_db():
    # Ouverture d'une session
    db = SessionLocal()
    try:
        yield db   # on fournit la session à la route FastAPI
    finally:
        db.close() # fermeture après usage

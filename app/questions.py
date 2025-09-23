# ============================================================
# questions.py - Récupération des questions depuis MongoDB
# ============================================================

from pymongo import MongoClient
import os

# Connexion Mongo (via variable d'environnement si dispo)
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URL)

# Sélection de la base et de la collection
db = client.quizdb
collection = db.questions

def get_questions(limit: int = 5):
    """
    Récupère les questions depuis MongoDB.
    Retourne une liste de dictionnaires compatibles avec le front.
    """
    cursor = collection.find().limit(limit)
    questions = []

    for doc in cursor:
        # On force les clés attendues par le front
        q = {
            "question": doc.get("question", ""),
            "theme": doc.get("theme", "Général"),
            "niveau": doc.get("niveau", "Facile"),
            "choix": doc.get("choix", []),
            "correct": doc.get("correct", [])
        }
        questions.append(q)

    return questions

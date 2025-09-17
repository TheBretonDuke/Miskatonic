# ============================================================
# app/questions.py
#
# Routes pour interagir avec les questions (MongoDB)
# ============================================================

from fastapi import APIRouter
from app.database import questions_collection  # connexion Mongo

# Création du routeur pour les questions
router = APIRouter()

@router.get("/")
def get_questions(limit: int = 5):
    """
    Récupère les X premières questions depuis MongoDB.
    - limit : nombre de questions à renvoyer (par défaut 5)
    """
    # Lecture dans MongoDB
    questions = list(questions_collection.find().limit(limit))
    
    # Conversion de l'_id Mongo en string (sinon JSON ne comprend pas)
    for q in questions:
        q["_id"] = str(q["_id"])
    
    return questions

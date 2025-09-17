# ============================================================
# app/questions.py
#
# Routes pour interagir avec les questions (MongoDB)
# ============================================================

from fastapi import APIRouter
from app.database import questions_collection

router = APIRouter()

@router.get("/")
def get_questions(limit: int = 5):
    """
    Récupère aléatoirement X questions depuis MongoDB.
    - limit : nombre de questions à renvoyer (par défaut 5)
    """
    docs = questions_collection.aggregate([{"$sample": {"size": limit}}])

    questions = []
    for q in docs:
        questions.append({
            "id": str(q["_id"]),
            "question": q["question"],
            "choix": q["choix"],
            "correct": q["bonnes_reponses"],  # toujours une liste
            "theme": q["theme"],
            "niveau": q["niveau"]
        })

    return questions

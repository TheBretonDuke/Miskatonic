# ============================================================
# questions.py - Récupération des questions depuis MongoDB
# ============================================================

from pymongo import MongoClient
from bson import ObjectId
from datetime import datetime
import os

# Connexion Mongo (via variable d'environnement si dispo)
MONGO_URL = os.getenv("MONGO_URL", "mongodb://quiz:quiz@localhost:27017/admin")
client = MongoClient(MONGO_URL)

# Sélection de la base et de la collection
db = client.quiz_db
collection = db.questions
quiz_sessions = db.quiz_sessions

def get_questions(limit: int = 5, theme: str | None = None):
    """
    Récupère un échantillon aléatoire de questions depuis MongoDB, avec filtre de thème optionnel.
    Retourne une liste de dictionnaires compatibles avec le front.
    """
    try:
        size = int(limit) if int(limit) > 0 else 5
    except Exception:
        size = 5

    # Construire le pipeline avec un éventuel filtre de thème
    pipeline = []
    match: dict = {}
    if theme:
        match["theme"] = theme
        pipeline.append({"$match": match})

    # Ajuster la taille si on a un filtre pour éviter erreur $sample > count
    try:
        if match:
            count = collection.count_documents(match)
            size = min(size, max(count, 0))
    except Exception:
        pass

    if size <= 0:
        return []

    pipeline.append({"$sample": {"size": size}})
    cursor = collection.aggregate(pipeline)

    questions = []
    for doc in cursor:
        q = {
            "question": doc.get("question", ""),
            "theme": doc.get("theme") or "Général",
            "test": doc.get("test") or "Quiz",
            "choix": doc.get("choix", []),
            "correct": doc.get("correct", []),
        }
        questions.append(q)

    return questions

def create_quiz_session(username: str, limit: int = 5, name: str | None = None, theme: str | None = None) -> tuple[str | None, list[dict]]:
    """Crée un quiz (échantillon aléatoire) et le sauvegarde dans quiz_sessions. Retourne (quiz_id, questions)."""
    questions = get_questions(limit, theme)
    if not questions:
        return None, []
    doc = {
        "user": username,
        "limit": int(limit),
        "created_at": datetime.utcnow(),
        "questions": questions,
    }
    if name:
        # Sanitize simple
        doc["name"] = str(name)[:120]
    if theme:
        doc["theme"] = str(theme)[:120]
    res = quiz_sessions.insert_one(doc)
    return str(res.inserted_id), questions

def get_quiz_session_by_id(quiz_id: str) -> dict | None:
    """Récupère un quiz sauvegardé par son id."""
    try:
        oid = ObjectId(quiz_id)
    except Exception:
        return None
    doc = quiz_sessions.find_one({"_id": oid})
    if not doc:
        return None
    return {
        "quiz_id": str(doc["_id"]),
        "user": doc.get("user"),
        "name": doc.get("name"),
        "theme": doc.get("theme"),
        "limit": doc.get("limit"),
        "created_at": doc.get("created_at").isoformat() if doc.get("created_at") else None,
        "questions": doc.get("questions", []),
    }

def delete_quiz_session(quiz_id: str) -> int:
    """Supprime une session de quiz. Retourne le nombre supprimé (0 ou 1)."""
    try:
        oid = ObjectId(quiz_id)
    except Exception:
        return 0
    res = quiz_sessions.delete_one({"_id": oid})
    return int(res.deleted_count)

def list_quiz_sessions(user: str | None = None, max_items: int = 50) -> list[dict]:
    """Liste des sessions de quiz (récentes), éventuellement filtrées par utilisateur."""
    filt = {"user": user} if user else {}
    cursor = quiz_sessions.find(filt).sort("created_at", -1).limit(int(max_items))
    out: list[dict] = []
    for doc in cursor:
        out.append({
            "quiz_id": str(doc.get("_id")),
            "user": doc.get("user"),
            "name": doc.get("name"),
            "theme": doc.get("theme"),
            "limit": doc.get("limit"),
            "created_at": doc.get("created_at").isoformat() if doc.get("created_at") else None,
            "count": len(doc.get("questions", [])),
            "preview": (doc.get("questions", [{}])[0] or {}).get("question", "")[:100]
        })
    return out

def list_themes() -> list[str]:
    """Retourne la liste triée des thèmes existants."""
    try:
        vals = collection.distinct("theme")
        return sorted([v for v in vals if isinstance(v, str) and v.strip()])
    except Exception:
        return []
    
def list_tests() -> list[str]:
    """Retourne la liste triée des tests existants."""
    try:
        vals = collection.distinct("test")
        return sorted([v for v in vals if isinstance(v, str) and v.strip()])
    except Exception:
        return []

def add_question(doc: dict) -> bool:
    """Ajoute une question dans MongoDB. doc doit contenir question, theme, test, choix, correct."""
    required = {"question", "choix", "correct"}
    if not required.issubset(doc.keys()):
        return False
    if not isinstance(doc.get("choix", []), list) or not isinstance(doc.get("correct", []), list):
        return False
    # Normaliser quelques champs
    doc.setdefault("theme", "Général")
    doc.setdefault("test", "Quiz")
    try:
        collection.insert_one(doc)
        return True
    except Exception:
        return False

def delete_question_by_text(question_text: str) -> int:
    """Supprime les questions dont le champ question correspond exactement."""
    if not question_text:
        return 0
    try:
        res = collection.delete_many({"question": question_text})
        return int(res.deleted_count)
    except Exception:
        return 0

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from app.database import init_db, create_user, authenticate_user, get_user_role
from app.questions import (
    get_questions,
    add_question,
    delete_question_by_text,
    collection,
    create_quiz_session,
    get_quiz_session_by_id,
    delete_quiz_session,
    list_quiz_sessions,
    list_themes,
    list_tests
)

# --- INITIALISATION ---
app = FastAPI()
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELS ---
class Question(BaseModel):
    question: str
    theme: str
    test: str
    choix: List[str]
    correct: List[str]

class UserIn(BaseModel):
    username: str
    password: str
    role: str = "prof"  # 👈 rôle optionnel à l'inscription

class AnswerIn(BaseModel):
    username: str
    quiz_id: str | None = None
    question: str
    reponse: List[str]

# --- ROUTES ---

@app.get("/questions", response_model=List[Question])
def get_questions_route(limit: int = 5, theme: str | None = None):
    questions = get_questions(limit=limit, theme=theme)
    if not questions:
        raise HTTPException(status_code=500, detail="Aucune question disponible")
    return questions

@app.post("/register")
def register(user: UserIn):
    """Créer un nouvel utilisateur (stocké en SQLite)"""
    ok = create_user(user.username, user.password, user.role)
    if not ok:
        raise HTTPException(status_code=400, detail="Utilisateur déjà existant")
    return {"message": f"Utilisateur {user.username} créé avec succès (rôle={user.role})"}

@app.post("/login")
def login(user: UserIn):
    """Authentifier un utilisateur (SQLite)"""
    ok, role = authenticate_user(user.username, user.password)
    if ok:
        return {"message": "Connexion réussie", "role": role}
    raise HTTPException(status_code=401, detail="Identifiants invalides")

@app.post("/answer")
def answer(ans: AnswerIn):
    q = collection.find_one({"question": ans.question})
    if not q:
        raise HTTPException(status_code=404, detail="Question inconnue")

    is_correct = (set(ans.reponse) == set(q.get("correct", [])))
    return {"correct": is_correct}

# --- QUIZ sessions ---
class QuizCreateIn(BaseModel):
    username: str
    limit: int = 5
    name: str | None = None
    theme: str | None = None
    test: str | None = None

@app.post("/quiz/create")
def quiz_create(body: QuizCreateIn):
    if body.limit not in (5, 10):
        raise HTTPException(status_code=400, detail="Limite invalide (5 ou 10)")
    role = get_user_role(body.username)
    if role not in ("prof", "admin"):
        raise HTTPException(status_code=403, detail="Création réservée aux profs/admins")
    quiz_id, questions = create_quiz_session(body.username, body.limit, body.name, body.theme)
    if not quiz_id:
        raise HTTPException(status_code=500, detail="Impossible de créer le quiz")
    return {"quiz_id": quiz_id, "questions": questions, "limit": body.limit, "name": body.name, "theme": body.theme}

@app.get("/quiz/{quiz_id}")
def quiz_get(quiz_id: str):
    doc = get_quiz_session_by_id(quiz_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Quiz introuvable")
    return doc

@app.delete("/quiz/{quiz_id}")
def quiz_delete(quiz_id: str, username: str):
    doc = get_quiz_session_by_id(quiz_id)
    if not doc:
        raise HTTPException(status_code=404, detail="Quiz introuvable")
    # Simple ownership/role check: le créateur peut supprimer. Un admin/prof pourrait être autorisé aussi si désiré.
    if doc.get("user") != username:
        # Autoriser admin et prof à supprimer
        role = get_user_role(username)
        if role not in ("admin", "prof"):
            raise HTTPException(status_code=403, detail="Non autorisé")
    deleted = delete_quiz_session(quiz_id)
    return {"deleted": deleted}

@app.get("/quiz")
def quiz_list(username: str, max_items: int = 50, scope: str | None = None):
    """
    Liste des sessions de quiz.
    - admin: scope=all pour tout voir, sinon par défaut les siens
    - prof: uniquement les siens
    - élève: 403
    """
    role = get_user_role(username)
    if role not in ("prof", "admin"):
        raise HTTPException(status_code=403, detail="Non autorisé")
    if role == "admin" and scope == "all":
        return list_quiz_sessions(None, max_items)
    return list_quiz_sessions(username, max_items)

@app.get("/themes", response_model=List[str])
def themes_list():
    return list_themes()

@app.get("/tests", response_model=List[str])
def tests_list():
    return list_tests()

@app.get("/themes_by_test/{test_name}", response_model=List[str])
def themes_by_test(test_name: str):
    """Retourne la liste des thèmes qui ont des questions pour ce test."""
    if not test_name:
        return list_themes()  # fallback : tous les thèmes
    try:
        vals = collection.distinct("theme", {"test": test_name})
        return sorted([v for v in vals if isinstance(v, str) and v.strip()])
    except Exception:
        return []
    
@app.get("/tests_by_theme/{theme}", response_model=List[str])
def tests_by_theme(theme: str):
    # Récupère seulement les tests présents pour ce thème
    try:
        vals = collection.distinct("test", {"theme": theme})
        return sorted([v for v in vals if isinstance(v, str) and v.strip()])
    except:
        return []

@app.get("/tests_by_theme/{theme}", response_model=List[str])
def tests_by_theme(theme: str):
    # Récupère seulement les tests présents pour ce thème
    try:
        vals = collection.distinct("test", {"theme": theme})
        return sorted([v for v in vals if isinstance(v, str) and v.strip()])
    except:
        return []


# --- ADMIN/PROF: Gestion des questions ---
class QuestionIn(BaseModel):
    username: str  # utilisateur effectuant l'action
    question: str
    theme: str | None = None
    test: str | None = None
    choix: List[str]
    correct: List[str]

def _assert_prof_or_admin(username: str):
    role = get_user_role(username)
    if role not in ("prof", "admin"):
        raise HTTPException(status_code=403, detail="Accès réservé aux profs/admins")

@app.get("/admin/questions", response_model=List[Question])
def admin_list_questions(username: str):
    _assert_prof_or_admin(username)
    # Liste jusqu'à 200 pour l'UI
    docs = collection.find().limit(200)
    out = []
    for doc in docs:
        out.append({
            "question": doc.get("question", ""),
            "theme": doc.get("theme", ""),
            "test": doc.get("test", ""),
            "choix": doc.get("choix", []),
            "correct": doc.get("correct", []),
        })
    return out

@app.post("/admin/questions")
def admin_add_question(q: QuestionIn):
    _assert_prof_or_admin(q.username)
    ok = add_question({
        "question": q.question,
        "theme": q.theme,
        "test": q.test,
        "choix": q.choix,
        "correct": q.correct,
    })
    if not ok:
        raise HTTPException(status_code=400, detail="Données invalides ou insertion échouée")
    return {"message": "Question ajoutée"}

@app.delete("/admin/questions")
def admin_delete_question(username: str, question: str):
    _assert_prof_or_admin(username)
    deleted = delete_question_by_text(question)
    if deleted == 0:
        raise HTTPException(status_code=404, detail="Aucune question supprimée")
    return {"deleted": deleted}

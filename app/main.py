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

# ============================================================================
# INITIALISATION
# ============================================================================

app = FastAPI(title="Miskatonic Quiz API", version="1.0.0")
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ============================================================================
# MODELS
# ============================================================================

class Question(BaseModel):
    question: str
    theme: str
    test: str
    choix: List[str]
    correct: List[str]

class UserCredentials(BaseModel):
    username: str
    password: str
    role: str = "prof"

class QuestionInput(BaseModel):
    username: str
    question: str
    theme: str | None = None
    test: str | None = None
    choix: List[str]
    correct: List[str]

class QuizInput(BaseModel):
    username: str
    limit: int = 5
    name: str | None = None
    theme: str | None = None

class AnswerInput(BaseModel):
    username: str
    quiz_id: str | None = None
    question: str
    reponse: List[str]

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================

def require_prof_or_admin(username: str):
    """Vérifie que l'utilisateur a les droits prof ou admin"""
    role = get_user_role(username)
    if role not in ("prof", "admin"):
        raise HTTPException(status_code=403, detail="Accès réservé aux professeurs et administrateurs")

# ============================================================================
# ROUTES AUTHENTIFICATION
# ============================================================================

@app.post("/register")
def register_user(user: UserCredentials):
    """Créer un nouveau compte utilisateur"""
    success = create_user(user.username, user.password, user.role)
    if not success:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris")
    return {"message": f"Compte créé avec succès (rôle: {user.role})"}

@app.post("/login")
def login_user(user: UserCredentials):
    """Connexion utilisateur"""
    success, role = authenticate_user(user.username, user.password)
    if not success:
        raise HTTPException(status_code=401, detail="Identifiants incorrects")
    return {"message": "Connexion réussie", "role": role}

# ============================================================================
# ROUTES QUESTIONS
# ============================================================================

@app.get("/questions", response_model=List[Question])
def get_questions_list(limit: int = 5, theme: str | None = None, admin: bool = False, username: str | None = None):
    """
    Récupérer des questions
    - Mode normal: échantillon aléatoire pour quiz
    - Mode admin: toutes les questions pour gestion (prof/admin uniquement)
    """
    if admin:
        if not username:
            raise HTTPException(status_code=400, detail="Nom d'utilisateur requis en mode admin")
        require_prof_or_admin(username)
        
        # Retourner toutes les questions (avec limite pour éviter surcharge)
        docs = collection.find().limit(200)
        questions = []
        for doc in docs:
            questions.append({
                "question": doc.get("question", ""),
                "theme": doc.get("theme") or "Général",
                "test": doc.get("test") or "Quiz",
                "choix": doc.get("choix", []),
                "correct": doc.get("correct", []),
            })
        return questions
    else:
        # Mode normal: échantillon aléatoire
        return get_questions(limit, theme)

@app.post("/questions")
def add_new_question(q: QuestionInput):
    """Ajouter une nouvelle question (prof/admin uniquement)"""
    require_prof_or_admin(q.username)
    
    success = add_question({
        "question": q.question,
        "theme": q.theme or "Général",
        "test": q.test or "Quiz",
        "choix": q.choix,
        "correct": q.correct,
    })
    
    if not success:
        raise HTTPException(status_code=400, detail="Erreur lors de l'ajout de la question")
    return {"message": "Question ajoutée avec succès"}

@app.delete("/questions")
def delete_question(username: str, question: str):
    """Supprimer une question (prof/admin uniquement)"""
    require_prof_or_admin(username)
    
    deleted_count = delete_question_by_text(question)
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Question non trouvée")
    return {"message": f"{deleted_count} question(s) supprimée(s)"}

# ============================================================================
# ROUTES QUIZ SESSIONS
# ============================================================================

@app.post("/quiz/create")
def create_quiz(quiz: QuizInput):
    """Créer une session de quiz (prof/admin uniquement)"""
    require_prof_or_admin(quiz.username)
    
    if quiz.limit not in (5, 10):
        raise HTTPException(status_code=400, detail="Nombre de questions invalide (5 ou 10 seulement)")
    
    quiz_id, questions = create_quiz_session(quiz.username, quiz.limit, quiz.name, quiz.theme)
    if not quiz_id:
        raise HTTPException(status_code=500, detail="Impossible de créer le quiz")
    
    return {
        "quiz_id": quiz_id,
        "questions": questions,
        "limit": quiz.limit,
        "name": quiz.name,
        "theme": quiz.theme
    }

@app.get("/quiz/{quiz_id}")
def get_quiz(quiz_id: str):
    """Récupérer une session de quiz par son ID"""
    quiz = get_quiz_session_by_id(quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz non trouvé")
    return quiz

@app.delete("/quiz/{quiz_id}")
def delete_quiz(quiz_id: str, username: str):
    """Supprimer une session de quiz"""
    quiz = get_quiz_session_by_id(quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz non trouvé")
    
    # Vérifier les permissions (créateur ou admin/prof)
    if quiz.get("user") != username:
        require_prof_or_admin(username)
    
    deleted = delete_quiz_session(quiz_id)
    return {"message": "Quiz supprimé", "deleted": deleted}

@app.get("/quiz")
def list_quizzes(username: str, max_items: int = 50, scope: str | None = None):
    """Lister les sessions de quiz (prof/admin uniquement)"""
    role = get_user_role(username)
    if role not in ("prof", "admin"):
        raise HTTPException(status_code=403, detail="Accès réservé aux professeurs et administrateurs")
    
    # Admin peut voir tous les quiz avec scope=all
    if role == "admin" and scope == "all":
        return list_quiz_sessions(None, max_items)
    
    # Sinon, seulement ses propres quiz
    return list_quiz_sessions(username, max_items)

# ============================================================================
# ROUTES UTILITAIRES
# ============================================================================

@app.get("/themes", response_model=List[str])
def get_themes():
    """Récupérer la liste des thèmes disponibles"""
    return list_themes()

@app.get("/tests", response_model=List[str])
def get_tests():
    """Récupérer la liste des tests disponibles"""
    return list_tests()

@app.get("/themes_by_test/{test_name}", response_model=List[str])
def get_themes_for_test(test_name: str):
    """Récupérer les thèmes disponibles pour un test donné"""
    if not test_name:
        return list_themes()
    
    try:
        themes = collection.distinct("theme", {"test": test_name})
        return sorted([t for t in themes if isinstance(t, str) and t.strip()])
    except Exception:
        return []

@app.get("/tests_by_theme/{theme}", response_model=List[str])
def get_tests_for_theme(theme: str):
    """Récupérer les tests disponibles pour un thème donné"""
    try:
        tests = collection.distinct("test", {"theme": theme})
        return sorted([t for t in tests if isinstance(t, str) and t.strip()])
    except Exception:
        return []

# ============================================================================
# ROUTES QUIZ (réponses)
# ============================================================================

@app.post("/answer")
def check_answer(answer: AnswerInput):
    """Vérifier si une réponse est correcte"""
    question_doc = collection.find_one({"question": answer.question})
    if not question_doc:
        raise HTTPException(status_code=404, detail="Question non trouvée")
    
    correct_answers = set(question_doc.get("correct", []))
    user_answers = set(answer.reponse)
    is_correct = (user_answers == correct_answers)
    
    return {"correct": is_correct}
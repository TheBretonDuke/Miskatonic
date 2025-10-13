"""
Routes de gestion des quiz
"""
from fastapi import APIRouter, HTTPException
from ..models import QuizInput
from ..utils import require_prof_or_admin
from ..database import get_user_role
from ..questions import (
    create_quiz_session,
    get_quiz_session_by_id,
    delete_quiz_session,
    list_quiz_sessions
)

router = APIRouter(prefix="/quiz", tags=["quiz"])


@router.post("/create")
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


@router.get("/{quiz_id}")
def get_quiz(quiz_id: str):
    """Récupérer une session de quiz par son ID"""
    quiz = get_quiz_session_by_id(quiz_id)
    if not quiz:
        raise HTTPException(status_code=404, detail="Quiz non trouvé")
    return quiz


@router.delete("/{quiz_id}")
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


@router.get("")
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
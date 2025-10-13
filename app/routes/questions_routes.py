"""
Routes de gestion des questions
"""
from fastapi import APIRouter, HTTPException
from typing import List
from ..models import Question, QuestionInput
from ..utils import require_prof_or_admin
from ..questions import get_questions, add_question, delete_question_by_text, collection

router = APIRouter(prefix="/questions", tags=["questions"])


@router.get("", 
    response_model=List[Question],
    summary="Récupérer des questions de quiz",
    description="""
    Endpoint principal pour récupérer des questions selon le contexte d'utilisation.
    
    **Deux modes d'utilisation :**
    
    ### Mode Normal (Étudiants)
    - `admin=false` (par défaut)
    - Retourne un échantillon aléatoire de questions
    - Filtrage possible par `theme`
    - Limite configurable avec `limit`
    
    ### Mode Administration (Prof/Admin)
    - `admin=true` + `username` requis
    - Retourne toutes les questions (jusqu'à 200)
    - Accès contrôlé par rôle utilisateur
    - Permet la gestion complète des questions
    
    **Exemples :**
    - `/questions?limit=10&theme=Mathématiques` : 10 questions de maths aléatoires
    - `/questions?admin=true&username=prof1` : Toutes les questions (si prof/admin)
    """,
    responses={
        200: {
            "description": "Liste des questions selon les critères",
            "content": {
                "application/json": {
                    "example": [
                        {
                            "question": "Quelle est la capitale de la France ?",
                            "theme": "Géographie", 
                            "test": "Culture générale",
                            "choix": ["Paris", "Lyon", "Marseille"],
                            "correct": ["Paris"]
                        }
                    ]
                }
            }
        },
        403: {"description": "Accès refusé (mode admin sans autorisation)"}
    }
)
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


@router.post("",
    summary="Ajouter une nouvelle question",
    description="""
    Permet aux professeurs et administrateurs d'ajouter de nouvelles questions à la base.
    
    **Prérequis :** Rôle `prof` ou `admin`
    
    **Champs obligatoires :**
    - `question` : Le texte de la question
    - `choix` : Liste des réponses possibles  
    - `correct` : Liste des bonnes réponses
    - `username` : Pour vérification des droits
    
    **Champs optionnels :**
    - `theme` : Défaut "Général"
    - `test` : Défaut "Quiz"
    
    **Note :** Les questions sont immédiatement disponibles pour la génération de quiz.
    """,
    responses={
        200: {"description": "Question ajoutée avec succès"},
        400: {"description": "Erreur dans les données fournies"},
        403: {"description": "Droits insuffisants (prof/admin requis)"}
    }
)
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


@router.delete("",
    summary="Supprimer une question",
    description="""
    Permet aux professeurs et administrateurs de supprimer des questions existantes.
    
    **Prérequis :** Rôle `prof` ou `admin`
    
    **Méthode :** Suppression par correspondance exacte du texte de la question.
    
    **⚠️ Attention :** Action irréversible ! La question sera définitivement supprimée de la base.
    """,
    responses={
        200: {"description": "Question(s) supprimée(s) avec succès"},
        404: {"description": "Question non trouvée"},
        403: {"description": "Droits insuffisants (prof/admin requis)"}
    }
)
def delete_question(username: str, question: str):
    """Supprimer une question (prof/admin uniquement)"""
    require_prof_or_admin(username)
    
    deleted_count = delete_question_by_text(question)
    if deleted_count == 0:
        raise HTTPException(status_code=404, detail="Question non trouvée")
    return {"message": f"{deleted_count} question(s) supprimée(s)"}
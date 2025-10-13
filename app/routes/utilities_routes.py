"""
Routes utilitaires (thèmes, tests, etc.)
"""
from fastapi import APIRouter, HTTPException
from typing import List
from ..models import AnswerInput
from ..questions import list_themes, list_tests, collection

router = APIRouter(tags=["utilitaires"])


@router.get("/themes", 
    response_model=List[str],
    summary="Liste des thèmes disponibles",
    description="""
    Retourne la liste de tous les thèmes présents dans la base de questions.
    
    **Utilisation :** Alimenter les filtres de sélection dans l'interface utilisateur.
    """,
    response_description="Liste alphabétique des thèmes uniques"
)
def get_themes():
    """Récupérer la liste des thèmes disponibles"""
    return list_themes()


@router.get("/tests", response_model=List[str])
def get_tests():
    """Récupérer la liste des tests disponibles"""
    return list_tests()


@router.get("/themes_by_test/{test_name}", response_model=List[str])
def get_themes_for_test(test_name: str):
    """Récupérer les thèmes disponibles pour un test donné"""
    if not test_name:
        return list_themes()
    
    try:
        themes = collection.distinct("theme", {"test": test_name})
        return sorted([t for t in themes if isinstance(t, str) and t.strip()])
    except Exception:
        return []


@router.get("/tests_by_theme/{theme}", response_model=List[str])
def get_tests_for_theme(theme: str):
    """Récupérer les tests disponibles pour un thème donné"""
    try:
        tests = collection.distinct("test", {"theme": theme})
        return sorted([t for t in tests if isinstance(t, str) and t.strip()])
    except Exception:
        return []


@router.post("/answer",
    summary="Vérifier une réponse de quiz",
    description="""
    Valide si la réponse d'un étudiant à une question est correcte.
    
    **Logique de validation :**
    - Comparaison exacte entre les réponses sélectionnées et les bonnes réponses
    - Support des questions à choix multiples
    - Retour booléen simple (correct/incorrect)
    
    **Exemple :** Si la bonne réponse est ["A", "C"] et que l'étudiant répond ["A", "C"], 
    le résultat sera `true`. Si il répond ["A"] ou ["A", "B", "C"], ce sera `false`.
    """,
    responses={
        200: {
            "description": "Résultat de la validation",
            "content": {
                "application/json": {
                    "example": {"correct": True}
                }
            }
        },
        404: {"description": "Question non trouvée dans la base"}
    }
)
def check_answer(answer: AnswerInput):
    """Vérifier si une réponse est correcte"""
    question_doc = collection.find_one({"question": answer.question})
    if not question_doc:
        raise HTTPException(status_code=404, detail="Question non trouvée")
    
    correct_answers = set(question_doc.get("correct", []))
    user_answers = set(answer.reponse)
    is_correct = (user_answers == correct_answers)
    
    return {"correct": is_correct}
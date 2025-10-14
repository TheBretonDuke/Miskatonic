"""
Modèles Pydantic pour l'API Miskatonic Quiz
"""
from pydantic import BaseModel, Field
from typing import List


class Question(BaseModel):
    """Modèle d'une question de quiz complète"""
    question: str = Field(..., description="Texte de la question", example="Quelle est la capitale de la France ?")
    theme: str = Field(..., description="Thème/matière de la question", example="Géographie")
    test: str = Field(..., description="Type de test/examen", example="Culture générale")
    choix: List[str] = Field(..., description="Liste des réponses possibles", example=["Paris", "Lyon", "Marseille", "Toulouse"])
    correct: List[str] = Field(..., description="Liste des bonnes réponses", example=["Paris"])


class UserCredentials(BaseModel):
    """Informations d'authentification utilisateur"""
    username: str = Field(..., description="Nom d'utilisateur unique", example="prof_martin")
    password: str = Field(..., description="Mot de passe (sera haché)", example="motdepasse123")
    role: str = Field(default="prof", description="Rôle utilisateur", example="prof", pattern="^(etudiant|prof|admin)$")


class QuestionInput(BaseModel):
    """Données pour créer une nouvelle question"""
    username: str = Field(..., description="Nom d'utilisateur (pour vérification des droits)", example="prof_martin")
    question: str = Field(..., description="Texte de la question", example="Combien font 2+2 ?")
    theme: str | None = Field(None, description="Thème de la question", example="Mathématiques")
    test: str | None = Field(None, description="Type de test", example="Calcul mental")
    choix: List[str] = Field(..., description="Réponses possibles", example=["3", "4", "5", "6"])
    correct: List[str] = Field(..., description="Bonnes réponses", example=["4"])


class QuizInput(BaseModel):
    """Paramètres de création d'un quiz"""
    username: str = Field(..., description="Créateur du quiz", example="prof_martin")
    limit: int = Field(default=5, description="Nombre de questions", example=10, ge=1, le=50)
    name: str | None = Field(None, description="Nom du quiz", example="Quiz de révision")
    theme: str | None = Field(None, description="Filtrage par thème", example="Mathématiques")


class AnswerInput(BaseModel):
    """Réponse d'un étudiant à une question"""
    username: str = Field(..., description="Nom de l'étudiant", example="etudiant_marie")
    quiz_id: str | None = Field(None, description="ID de session de quiz", example="quiz_123456")
    question: str = Field(..., description="Question à laquelle on répond", example="Combien font 2+2 ?")
    reponse: List[str] = Field(..., description="Réponses sélectionnées", example=["4"])


# --- Modèles pour la gestion des utilisateurs ---

class UserInfo(BaseModel):
    """Informations publiques d'un utilisateur"""
    username: str = Field(..., description="Nom d'utilisateur", example="prof_martin")
    role: str = Field(..., description="Rôle de l'utilisateur", example="prof")


class UserRoleUpdate(BaseModel):
    """Mise à jour du rôle d'un utilisateur"""
    admin_username: str = Field(..., description="Nom d'utilisateur admin (pour vérification)", example="admin")
    target_username: str = Field(..., description="Utilisateur à modifier", example="prof_martin") 
    new_role: str = Field(..., description="Nouveau rôle", example="admin", pattern="^(etudiant|prof|admin)$")


class PasswordUpdate(BaseModel):
    """Mise à jour du mot de passe"""
    username: str = Field(..., description="Nom d'utilisateur", example="prof_martin")
    current_password: str = Field(..., description="Mot de passe actuel", example="ancien_mdp")
    new_password: str = Field(..., description="Nouveau mot de passe", example="nouveau_mdp", min_length=6)


class UserDeletion(BaseModel):
    """Suppression d'un utilisateur"""
    admin_username: str = Field(..., description="Nom d'utilisateur admin (pour vérification)", example="admin")
    target_username: str = Field(..., description="Utilisateur à supprimer", example="prof_martin")
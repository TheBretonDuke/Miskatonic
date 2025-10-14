"""
Routes d'authentification et gestion des utilisateurs
"""
from fastapi import APIRouter, HTTPException
from typing import List
from ..models import UserCredentials, UserInfo, UserRoleUpdate, PasswordUpdate, UserDeletion
from ..database import (
    create_user, authenticate_user, get_user_role, 
    list_users, delete_user, update_user_role, 
    update_user_password, user_exists
)
from ..utils import require_admin

router = APIRouter(prefix="", tags=["authentification"])


@router.post("/register", 
    summary="Créer un nouveau compte utilisateur",
    description="""
    Permet de créer un nouveau compte utilisateur dans le système.
    
    **Rôles disponibles :**
    - `etudiant` : Peut passer des quiz uniquement
    - `prof` : Peut créer/modifier des questions et passer des quiz  
    - `admin` : Accès complet au système
    
    **Note :** Le mot de passe sera automatiquement haché avec bcrypt.
    """,
    response_description="Confirmation de création du compte"
)
def register_user(user: UserCredentials):
    """Créer un nouveau compte utilisateur"""
    success = create_user(user.username, user.password, user.role)
    if not success:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur déjà pris")
    return {"message": f"Compte créé avec succès (rôle: {user.role})"}


@router.post("/login",
    summary="Connexion utilisateur",
    description="""
    Authentifie un utilisateur avec ses identifiants.
    
    **Processus :**
    1. Vérification du nom d'utilisateur
    2. Validation du mot de passe haché
    3. Retour du rôle de l'utilisateur
    
    **Utilisation :** Stocker le rôle côté client pour contrôler l'accès aux fonctionnalités.
    """,
    response_description="Informations de connexion et rôle utilisateur"
)
def login_user(user: UserCredentials):
    """Connexion utilisateur"""
    success, role = authenticate_user(user.username, user.password)
    if not success:
        raise HTTPException(status_code=401, detail="Identifiants incorrects")
    return {"message": "Connexion réussie", "role": role}


# --- Gestion avancée des utilisateurs ---

@router.get("/users", 
    response_model=List[UserInfo],
    summary="Lister tous les utilisateurs",
    description="""
    Récupère la liste de tous les utilisateurs enregistrés dans le système.
    
    **Prérequis :** Rôle `admin` uniquement
    
    **Retour :** Liste des utilisateurs avec leur nom et rôle (sans les mots de passe)
    
    **Utilisation :** Interface d'administration pour voir qui a accès au système
    """,
    responses={
        200: {
            "description": "Liste des utilisateurs",
            "content": {
                "application/json": {
                    "example": [
                        {"username": "admin", "role": "admin"},
                        {"username": "prof_martin", "role": "prof"},
                        {"username": "etudiant_marie", "role": "etudiant"}
                    ]
                }
            }
        },
        403: {"description": "Accès refusé (admin requis)"}
    }
)
def list_all_users(admin_username: str):
    """Lister tous les utilisateurs (admin uniquement)"""
    require_admin(admin_username)
    users = list_users()
    return users


@router.delete("/users/{target_username}",
    summary="Supprimer un utilisateur",
    description="""
    Supprime définitivement un utilisateur du système.
    
    **Prérequis :** Rôle `admin` uniquement
    
    **⚠️ Attention :** Action irréversible ! L'utilisateur ne pourra plus se connecter.
    
    **Sécurité :** Un admin ne peut pas se supprimer lui-même pour éviter le verrouillage du système.
    """,
    responses={
        200: {"description": "Utilisateur supprimé avec succès"},
        404: {"description": "Utilisateur non trouvé"},
        403: {"description": "Accès refusé (admin requis)"},
        400: {"description": "Impossible de se supprimer soi-même"}
    }
)
def delete_user_endpoint(target_username: str, admin_username: str):
    """Supprimer un utilisateur (admin uniquement)"""
    require_admin(admin_username)
    
    # Empêcher l'admin de se supprimer lui-même
    if admin_username == target_username:
        raise HTTPException(status_code=400, detail="Impossible de se supprimer soi-même")
    
    # Vérifier que l'utilisateur existe
    if not user_exists(target_username):
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    success = delete_user(target_username)
    if not success:
        raise HTTPException(status_code=500, detail="Erreur lors de la suppression")
    
    return {"message": f"Utilisateur '{target_username}' supprimé avec succès"}


@router.put("/users/{target_username}/role",
    summary="Modifier le rôle d'un utilisateur",
    description="""
    Met à jour le rôle d'un utilisateur existant.
    
    **Prérequis :** Rôle `admin` uniquement
    
    **Rôles disponibles :**
    - `etudiant` : Accès limité aux quiz
    - `prof` : Gestion des questions et quiz
    - `admin` : Accès complet au système
    
    **Sécurité :** Un admin ne peut pas modifier son propre rôle pour éviter la perte de privilèges.
    """,
    responses={
        200: {"description": "Rôle modifié avec succès"},
        404: {"description": "Utilisateur non trouvé"},
        403: {"description": "Accès refusé (admin requis)"},
        400: {"description": "Rôle invalide ou impossible de modifier son propre rôle"}
    }
)
def update_user_role_endpoint(target_username: str, role_update: UserRoleUpdate):
    """Modifier le rôle d'un utilisateur (admin uniquement)"""
    require_admin(role_update.admin_username)
    
    # Empêcher l'admin de modifier son propre rôle
    if role_update.admin_username == target_username:
        raise HTTPException(status_code=400, detail="Impossible de modifier son propre rôle")
    
    # Vérifier que l'utilisateur existe
    if not user_exists(target_username):
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    success = update_user_role(target_username, role_update.new_role)
    if not success:
        raise HTTPException(status_code=400, detail="Rôle invalide ou erreur lors de la mise à jour")
    
    return {"message": f"Rôle de '{target_username}' mis à jour vers '{role_update.new_role}'"}


@router.put("/users/{username}/password",
    summary="Changer son mot de passe",
    description="""
    Permet à un utilisateur de changer son mot de passe.
    
    **Sécurité :**
    - Nécessite le mot de passe actuel pour confirmation
    - Le nouveau mot de passe doit faire au moins 6 caractères
    - Le mot de passe est automatiquement haché avec bcrypt
    
    **Utilisation :** Auto-gestion par l'utilisateur (pas besoin d'être admin)
    """,
    responses={
        200: {"description": "Mot de passe modifié avec succès"},
        404: {"description": "Utilisateur non trouvé"},
        401: {"description": "Mot de passe actuel incorrect"},
        400: {"description": "Nouveau mot de passe invalide"}
    }
)
def change_password(username: str, password_update: PasswordUpdate):
    """Changer le mot de passe d'un utilisateur"""
    # Vérifier que l'utilisateur correspond
    if username != password_update.username:
        raise HTTPException(status_code=400, detail="Nom d'utilisateur incohérent")
    
    # Vérifier que l'utilisateur existe et que le mot de passe actuel est correct
    success, _ = authenticate_user(username, password_update.current_password)
    if not success:
        raise HTTPException(status_code=401, detail="Mot de passe actuel incorrect")
    
    # Mettre à jour le mot de passe
    success = update_user_password(username, password_update.new_password)
    if not success:
        raise HTTPException(status_code=500, detail="Erreur lors de la mise à jour du mot de passe")
    
    return {"message": "Mot de passe modifié avec succès"}


@router.get("/users/{username}",
    response_model=UserInfo,
    summary="Récupérer les informations d'un utilisateur",
    description="""
    Récupère les informations publiques d'un utilisateur spécifique.
    
    **Accès :**
    - Tout utilisateur peut voir ses propres informations
    - Les admins peuvent voir les informations de tous les utilisateurs
    
    **Données retournées :** Nom d'utilisateur et rôle (pas de mot de passe)
    """,
    responses={
        200: {
            "description": "Informations de l'utilisateur",
            "content": {
                "application/json": {
                    "example": {"username": "prof_martin", "role": "prof"}
                }
            }
        },
        404: {"description": "Utilisateur non trouvé"},
        403: {"description": "Accès refusé"}
    }
)
def get_user_info(username: str, requesting_user: str):
    """Récupérer les informations d'un utilisateur"""
    # Vérifier que l'utilisateur existe
    if not user_exists(username):
        raise HTTPException(status_code=404, detail="Utilisateur non trouvé")
    
    # Contrôle d'accès : utilisateur lui-même ou admin
    requesting_role = get_user_role(requesting_user)
    if requesting_user != username and requesting_role != "admin":
        raise HTTPException(status_code=403, detail="Accès refusé")
    
    role = get_user_role(username)
    return {"username": username, "role": role}
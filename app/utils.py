"""
Utilitaires et fonctions d'aide pour l'API
"""
from fastapi import HTTPException
from .database import get_user_role


def require_prof_or_admin(username: str):
    """Vérifie que l'utilisateur a les droits prof ou admin"""
    role = get_user_role(username)
    if role not in ("prof", "admin"):
        raise HTTPException(status_code=403, detail="Accès réservé aux professeurs et administrateurs")


def require_admin(username: str):
    """Vérifie que l'utilisateur a les droits admin uniquement"""
    role = get_user_role(username)
    if role != "admin":
        raise HTTPException(status_code=403, detail="Accès réservé aux administrateurs")
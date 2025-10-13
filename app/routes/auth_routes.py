"""
Routes d'authentification
"""
from fastapi import APIRouter, HTTPException
from ..models import UserCredentials
from ..database import create_user, authenticate_user

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
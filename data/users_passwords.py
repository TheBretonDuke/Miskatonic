# ============================================================
# users_passwords.py - Gestion des mots de passe (bcrypt)
# ============================================================
# Objectifs :
#   - Centraliser le hachage et la vérification des mots de passe
#   - Ne pas gérer la base SQLite ici (ça se fait dans database.py)
#   - Fournir deux fonctions simples :
#       -> hash_password()
#       -> verify_password()
# ============================================================

import bcrypt

# ---------- HACHAGE ----------
def hash_password(password: str) -> str:
    """
    Hache un mot de passe en utilisant bcrypt.
    - Entrée : mot de passe en clair (str)
    - Sortie : hash (str, encodé en UTF-8)
    """
    hashed = bcrypt.hashpw(password.encode("utf-8"), bcrypt.gensalt())
    return hashed.decode("utf-8")   # on retourne une chaîne pour stockage en SQLite


# ---------- VÉRIFICATION ----------
def verify_password(password: str, hashed: str) -> bool:
    """
    Vérifie qu’un mot de passe correspond à un hash bcrypt.
    - password : mot de passe en clair
    - hashed   : hash bcrypt (str) récupéré en DB
    Retourne :
        True si le mot de passe est correct, False sinon
    """
    return bcrypt.checkpw(password.encode("utf-8"), hashed.encode("utf-8"))

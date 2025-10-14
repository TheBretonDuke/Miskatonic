import sqlite3
from app.users_passwords import hash_password, verify_password

DB_PATH = "data/users.db"

# --- Création de la table users avec rôles ---
def init_db():
    """Initialise la base SQLite (crée la table users si elle n'existe pas)."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute('''
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            username TEXT UNIQUE NOT NULL,
            password TEXT NOT NULL,
            role TEXT NOT NULL CHECK(role IN ('prof', 'admin', 'eleve')) DEFAULT 'prof'
        )
    ''')
    conn.commit()
    conn.close()

# --- Création utilisateur ---
def create_user(username: str, password: str, role: str = "prof") -> bool:
    """
    Ajoute un utilisateur en SQLite.
    Retourne False si l'utilisateur existe déjà.
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    # Vérifier si le username existe déjà
    cur.execute("SELECT * FROM users WHERE username=?", (username,))
    if cur.fetchone():
        conn.close()
        return False

    # Hash du mot de passe
    hashed = hash_password(password)

    # Insertion du nouvel utilisateur avec rôle
    cur.execute(
        "INSERT INTO users (username, password, role) VALUES (?, ?, ?)",
        (username, hashed, role)
    )
    conn.commit()
    conn.close()
    return True

# --- Authentification ---
def authenticate_user(username: str, password: str) -> tuple[bool, str | None]:
    """
    Vérifie si le couple username/password est correct.
    Retourne (True, role) si ok, sinon (False, None).
    """
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()

    cur.execute("SELECT password, role FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    conn.close()

    if not row:
        return False, None

    stored_password, role = row
    if verify_password(password, stored_password):
        return True, role
    return False, None

# --- Rôle d'un utilisateur ---
def get_user_role(username: str) -> str | None:
    """Retourne le rôle de l'utilisateur (prof/admin/eleve) ou None si inconnu."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT role FROM users WHERE username=?", (username,))
    row = cur.fetchone()
    conn.close()
    if not row:
        return None
    return row[0]


# --- Gestion complète des utilisateurs ---
def list_users() -> list[dict]:
    """Retourne la liste de tous les utilisateurs (sans les mots de passe)."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT username, role FROM users ORDER BY username")
    rows = cur.fetchall()
    conn.close()
    return [{"username": row[0], "role": row[1]} for row in rows]


def delete_user(username: str) -> bool:
    """Supprime un utilisateur. Retourne True si succès."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("DELETE FROM users WHERE username=?", (username,))
    deleted = cur.rowcount > 0
    conn.commit()
    conn.close()
    return deleted


def update_user_role(username: str, new_role: str) -> bool:
    """Met à jour le rôle d'un utilisateur. Retourne True si succès."""
    if new_role not in ("etudiant", "prof", "admin"):
        return False
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE users SET role=? WHERE username=?", (new_role, username))
    updated = cur.rowcount > 0
    conn.commit()
    conn.close()
    return updated


def update_user_password(username: str, new_password: str) -> bool:
    """Met à jour le mot de passe d'un utilisateur. Retourne True si succès."""
    hashed = hash_password(new_password)
    
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("UPDATE users SET password_hash=? WHERE username=?", (hashed, username))
    updated = cur.rowcount > 0
    conn.commit()
    conn.close()
    return updated


def user_exists(username: str) -> bool:
    """Vérifie si un utilisateur existe. Retourne True si il existe."""
    conn = sqlite3.connect(DB_PATH)
    cur = conn.cursor()
    cur.execute("SELECT 1 FROM users WHERE username=?", (username,))
    exists = cur.fetchone() is not None
    conn.close()
    return exists

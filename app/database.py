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

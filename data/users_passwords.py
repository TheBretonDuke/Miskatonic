import sqlite3
import bcrypt

# Connexion à la base SQLite
conn = sqlite3.connect('./users.db')
cursor = conn.cursor()

# Création de la table
# cursor.execute('''CREATE TABLE IF NOT EXISTS users (
#    id INTEGER PRIMARY KEY AUTOINCREMENT,
#     username TEXT UNIQUE NOT NULL,
#     password_hash BLOB NOT NULL,
#     role TEXT NOT NULL CHECK(role IN ('prof', 'admin'))
# )''')
# (role IN ('prof', 'admin') = le champ role ne peut contenir que les valeurs prof ou admin (et pas élève)


# Ajout d'un utilisateur
def add_user(username, password, role='prof'):  # rôle par défaut, possible d'ajouter des admins plus tard
    # hachage du mot de passe (encode du mdp en bytes, génération d'un sel)
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    # insertion du username et mdp haché dans la base
    cursor.execute('INSERT INTO users (username, password_hash, role) VALUES (?, ?, ?)', (username, hashed, role))
    conn.commit()
    print(f"Utilisateur '{username}' ajouté avec succès.")

# Vérifier le mot de passe
def verify_user(username, password):
    # on récupère le mdp haché associé au username
    cursor.execute('SELECT password_hash FROM users WHERE username = ?', (username,))
    result = cursor.fetchone()
    if result:
        # on encode le mdp saisi
        # checkpw() compare ce mdp avec le hash stocké
        # L'utilisateur existe, on vérifie le mot de passe
        if bcrypt.checkpw(password.encode('utf-8'), result[0]):
            print("Connexion réussie : mot de passe correct.")
            return True
        else:
            print("Mot de passe incorrect.")
            return False
    else:
        # Aucun utilisateur trouvé
        print(f"Utilisateur '{username}' non trouvé dans la base.")
        return False


# === tests ====

# Ajout d'un utilisateur :
add_user("bob", "bruce0123")

# vérification avec le bon mdp
#verify_user("simon", "monSuperMotDePasse")
#verify_user("lucie", "bruce0123")

# vérification avec un mauvais mot de passe
#verify_user("simon", "blabla")
#verify_user("bob", "012302145vfz")

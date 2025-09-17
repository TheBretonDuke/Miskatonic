# =============================================
# ETL pour transformer le fichier questions.csv
# et l'insérer dans MongoDB
#
# E = Extract (extraction des données brutes CSV)
# T = Transform (nettoyage et mise en forme)
# L = Load (chargement dans MongoDB)
# =============================================

import pandas as pd                # Librairie pour manipuler facilement les CSV
from pymongo import MongoClient    # Librairie pour se connecter à MongoDB

# ========== 1. EXTRACT ==========
# On charge le fichier CSV dans un DataFrame (df) Pandas
# Chaque ligne correspond à une question avec ses réponses
df = pd.read_csv("data/questions.csv")

# ========== 2. TRANSFORM ==========
documents = []  # Liste où on va stocker les questions transformées

# On parcourt chaque ligne du CSV
for _, row in df.iterrows():
    # ---- a) Construire la liste des choix ----
    # On prend les colonnes responseA, responseB, responseC, responseD
    # et on ignore les NaN (réponses vides)
    choix = [
        row[c]
        for c in ["responseA", "responseB", "responseC", "responseD"]
        if pd.notna(row[c])
    ]
    
    # ---- b) Identifier la bonne réponse ----
    # Dans le CSV, "correct" contient une lettre (A, B, C ou D)
    # On traduit cette lettre en un index (0 pour A, 1 pour B, etc.)
    index_map = {"A": 0, "B": 1, "C": 2, "D": 3}
    correct_letter = row["correct"]  # ex: "A"
    bonne_reponse = None
    
    # Vérifier que la lettre existe et que l'index correspond bien à une réponse
    if correct_letter in index_map and index_map[correct_letter] < len(choix):
        bonne_reponse = choix[index_map[correct_letter]]
    
    # ---- c) Construire un dictionnaire propre ----
    # C'est le format final qu'on veut insérer dans MongoDB
    doc = {
        "question": row["question"],        # Texte de la question
        "choix": choix,                     # Liste des réponses possibles
        "bonne_reponse": bonne_reponse,     # Réponse correcte (texte)
        "theme": row["subject"],            # Thème (ex: BDD, réseau...)
        "niveau": row["use"]                # Niveau (ici "Test de positionnement")
    }
    
    # Ajouter ce document à notre liste
    documents.append(doc)

# ========== 3. LOAD ==========
# Connexion à MongoDB (il doit tourner en local sur le port 27017)
client = MongoClient("mongodb://localhost:27017/")

# On choisit la base "quizdb"
db = client.quizdb

# On choisit (ou crée automatiquement) la collection "questions"
collection = db.questions

# Supprimer d'abord les anciennes données pour éviter les doublons
collection.delete_many({})

# Insérer tous les documents transformés
collection.insert_many(documents)

# Petit message pour confirmer
print(f"{len(documents)} questions insérées dans MongoDB. Franchement tu gères bro'")

# ============================================================
# ETL - Chargement des questions CSV vers MongoDB
# ============================================================
# Objectif :
#   - Lire un fichier CSV contenant les questions
#   - Transformer chaque ligne en document JSON
#   - Insérer le tout dans une collection MongoDB
#
# Remarques :
#   - Supporte les QCM (plusieurs bonnes réponses possibles)
#   - Nettoie la collection avant d’insérer (on repart à zéro)
#   - Clés compatibles avec le frontend (questions.html / quiz.html)
# ============================================================

# ---------- IMPORTS ----------
import os               # pour récupérer des variables d'environnement (ex: URL Mongo)
import pandas as pd     # pour lire et manipuler le CSV
from pymongo import MongoClient   # driver pour se connecter à MongoDB

# ---------- 1. EXTRACT ----------
# On lit le fichier CSV qui contient les questions
# (colonnes attendues : question, subject, use, responseA...responseD, correct)
df = pd.read_csv("data/questions.csv")

# ---------- 2. TRANSFORM ----------
# On prépare une liste vide qui va contenir tous les documents à insérer dans Mongo
documents = []

# On mappe les lettres (A,B,C,D) vers les indices de la liste des choix
index_map = {"A": 0, "B": 1, "C": 2, "D": 3}

# On parcourt toutes les lignes du CSV
for _, row in df.iterrows():
    # a) Construire la liste des choix possibles
    # Exemple : ["Narsil", "Andúril", "Glamdring"]
    choix = [
        row[c]
        for c in ["responseA", "responseB", "responseC", "responseD"]
        if pd.notna(row[c])  # on évite les cases vides
    ]

    # b) Extraire la ou les bonnes réponses
    # La colonne "correct" contient des lettres (ex: "A" ou "A,C")
    correct_letters = str(row.get("correct", "")).split(",")
    correct = []  # liste qui contiendra les bonnes réponses sous forme de texte

    # On traduit les lettres en réponses réelles
    for letter in correct_letters:
        letter = letter.strip()  # on enlève les espaces
        if letter in index_map and index_map[letter] < len(choix):
            correct.append(choix[index_map[letter]])

    # c) Construire le document final au format JSON
    doc = {
        "question": row["question"],   # texte de la question
        "choix": choix,                # toutes les options possibles
        "correct": correct,            # une ou plusieurs bonnes réponses
        "theme": row["subject"],       # thème (matière, domaine)
        "niveau": row["use"]           # niveau de difficulté
    }

    # d) Ajouter le document à la liste
    documents.append(doc)

# ---------- 3. LOAD ----------
# Connexion à MongoDB
# On utilise une variable d'environnement pour être flexible
MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
client = MongoClient(MONGO_URL)

# On sélectionne la base et la collection
db = client.quizdb
collection = db.questions

# a) On vide la collection pour repartir à zéro
collection.delete_many({})

# b) On insère tous les documents d’un coup
if documents:
    collection.insert_many(documents)

# c) On affiche un message de confirmation
count = collection.count_documents({})
print(f"✅ Base Mongo prête : {count} questions insérées.")

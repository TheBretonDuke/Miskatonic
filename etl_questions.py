# =============================================
# ETL pour transformer le fichier questions.csv
# et l'insérer dans MongoDB
# =============================================

import pandas as pd
from pymongo import MongoClient

# 1. EXTRACT
df = pd.read_csv("data/questions.csv")

# 2. TRANSFORM
documents = []
for _, row in df.iterrows():
    # a) Liste des choix
    choix = [row[c] for c in ["responseA", "responseB", "responseC", "responseD"] if pd.notna(row[c])]

    # b) Liste des bonnes réponses (peut contenir 1 ou plusieurs lettres)
    index_map = {"A": 0, "B": 1, "C": 2, "D": 3}
    correct_letters = str(row["correct"]).split(",")  # ex: "A" ou "A,C"
    bonnes_reponses = []

    for letter in correct_letters:
        letter = letter.strip()
        if letter in index_map and index_map[letter] < len(choix):
            bonnes_reponses.append(choix[index_map[letter]])

    # c) Document Mongo
    doc = {
        "question": row["question"],
        "choix": choix,
        "bonnes_reponses": bonnes_reponses,  # 👈 liste au lieu d’une seule valeur
        "theme": row["subject"],
        "niveau": row["use"]
    }
    documents.append(doc)

# 3. LOAD
client = MongoClient("mongodb://localhost:27017/")
db = client.quizdb
collection = db.questions
collection.delete_many({})
collection.insert_many(documents)

print(f"{len(documents)} questions insérées dans MongoDB (QCM supportés).")

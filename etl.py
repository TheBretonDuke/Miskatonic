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
import pandas as pd
import re
from pymongo import MongoClient
 
 
# ---------- 1. EXTRACT ----------
df = pd.read_csv("data/questions.csv")
 
 
# ---------- 2. TRANSFORM ----------
# On garde uniquement les questions avec une réponse correcte renseignée
df = df[df["correct"].notna()]
 
# on crée un dictionnaire qui associe chaque lettre de réponse à sa position dans la liste choix
index_map = {"A": 0, "B": 1, "C": 2, "D": 3}
# on crée une liste vide qui va contenir tous les dictionnaires, un par question
documents = []
 
# on parcourt chaque ligne de df (en ignorant l'index du df, pas utile ici)
for _, row in df.iterrows():
    ## Liste des réponses possibles
    # on parcourt les colonnes "responseA" à "D" et on garde celles qui ne sont pas NaN
    choix = [row[c] for c in ["responseA", "responseB", "responseC", "responseD"] if pd.notna(row[c])]
 
    ## Liste des bonnes réponses (peut contenir 1 ou plusieurs lettres)
    # on récupère les lettres des bonnes réponses
    # on transforme "A,C" ou "A C" en ["A", "C"]
    correct_letters = re.split(r"[,\s]+", str(row["correct"]).strip(","))
    # on initialise une liste vide pour stocker les textes des bonnes réponses
    bonnes_reponses = []
 
    # on parcourt chaque lettre
    for letter in correct_letters:
        # on enlève les espaces éventuels
        letter = letter.strip()
        # on vérifie que la lettre est bien dans index_map
        # et que l'indice ne dépasse pas la taille de choix
        if letter in index_map and index_map[letter] < len(choix):
            # on ajoute le texte de la bonne réponse dans la liste bonne_reponses
            bonnes_reponses.append(choix[index_map[letter]])
 
 
# Construction du dictionnaire final pour chaque question
    # on ajoute aussi les colonnes "subject", "use" et "remark"
    # on récupère la valeur de la colonne renseignée entre ()
    # si valeur manquante = ça renvoie None
    document = {
        "question": row["question"],
        "theme": row.get("subject", "Général"),
        "niveau": "Facile",  # Par défaut, on peut ajuster selon vos besoins
        "choix": choix,
        "correct": bonnes_reponses
    }
 
    # on ajoute ce dictionnaire à la liste documents
    documents.append(document)
 
# On transforme la liste documents en df_clean
df_clean = pd.DataFrame(documents)
 
 
##### Gérer plusieurs questions avec le même intutilé
 
# on ajoute une colonne temporaire "question_clean"
# pour obtenir une version plus uniforme des questions
df_clean["question_clean"] = (
    df_clean["question"]        # on sélectionne la colonne question du df_clean
    .str.strip()                # on enlève les espaces
    .str.rstrip(":")            # on enlève les ":" à la fin
    .str.replace(r"\s+", " ", regex=True)  # on remplace les espaces multiples par un seul
)
 
# on repère les questions en plusieurs exemplaires dans le df_clean
questions_a_fusionner = (
    df_clean["question_clean"]  
    .value_counts()             # on compte combien de fois chaque question apparaît
    .loc[lambda x: x > 1]       # on garde uniquement celles qui apparaissent plus d’une fois
    .index.tolist()             # on récupère la liste des intitulés concernés
)
 
# on initialise une liste pour les nouvelles lignes fusionnées
lignes_fusionnees = []
# on construit un masque booléen qui permettra de marquer les lignes à supprimer plus tard
masque_total = pd.Series(False, index=df_clean.index)
# à chaque tour de boucle, on mettra certains index à True pour les marquer comme "à supprimer"
 
# on boucle sur chaque question à fusionner
for question in questions_a_fusionner:
    # on extrait toutes les lignes du df_clean qui correspondent à cette question
    groupe = df_clean[df_clean["question_clean"] == question]
   
    # on fusionne les réponses et on supprime les doublons
    merged_choix = sum(groupe["choix"], [])
    merged_choix = list(dict.fromkeys(merged_choix))
   
    # on fusionne les bonnes réponses et on supprime les doublons
    merged_correct = sum(groupe["correct"], [])
    merged_correct = list(dict.fromkeys(merged_correct))
   
    # on crée une nouvelle ligne
    new_row = {
        "question": question,
        "theme": groupe.iloc[0].get("theme", "Général"),
        "niveau": groupe.iloc[0].get("niveau", "Facile"),
        "choix": merged_choix,
        "correct": merged_correct
    }
 
    # on ajoute cette ligne à la liste des lignes fusionnées
    lignes_fusionnees.append(new_row)
   
    # Mise à jour du masque
    # "|"" met à True les lignes qui correspondent à la question en cours de fusion
    # pour les marquer comme "à supprimer"
    masque_total |= df_clean["question_clean"].str.strip() == question.strip()
 
 
# on met à jour df_clean
# ~masque_total : on inverse le masque pour ne garder que les lignes qu’on n’a pas fusionnées
df_clean = df_clean[~masque_total]
# on transforme la liste "lignes_fusionnees" en df
# on concatène df_clean et le df avec les lignes fusionnées
# on réindexe df_clean de façon propre, sans garder les anciens index
df_clean = pd.concat([df_clean, pd.DataFrame(lignes_fusionnees)], ignore_index=True)
 
# on supprime la colonne temporaire "question_clean"
df_clean.drop(columns=["question_clean"], inplace=True)
 
# on reconstruit documents à partir de df_clean
documents = df_clean.to_dict(orient="records")
 
 
# ---------- 3. LOAD ----------
# Connexion à MongoDB
# On utilise une variable d'environnement pour être flexible
# MONGO_URL = os.getenv("MONGO_URL", "mongodb://localhost:27017/")
client = MongoClient("mongodb://quiz:quiz@localhost:27017/admin")
 
# On sélectionne la base et la collection
db = client.quiz_db              
collection = db.questions
 
# Insertion dans MongoDB
collection.delete_many({})          # on vide la collection avant insertion
collection.insert_many(documents)   # on insère tous les documents
 
# On affiche un message de confirmation
count = collection.count_documents({})
print(f"Base Mongo prête : {count} questions insérées.")
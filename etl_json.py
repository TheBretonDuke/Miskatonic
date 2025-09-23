# =============================================
# ETL pour transformer le fichier questions.csv
# et générer un fichier json
# =============================================

import pandas as pd
import re
import json         # utile ?

# 1. EXTRACT
df = pd.read_csv("data/questions.csv")
#print (df)

# 2. TRANSFORM

# On garde uniquement les questions avec une réponse correcte renseignée
#(les 8 dernières question du fichier csv sont donc exclues)
df = df[df["correct"].notna()]


## garder le lien entre les lettres et le texte associé
# on crée un dictionnaire qui associe chaque lettre de réponse à sa position dans la liste choix
index_map = {"A": 0, "B": 1, "C": 2, "D": 3}
# liste vide qui va contenir tous les dictionnaires, un par question
documents = []

# on parcourt chaque ligne du df
# _ signifie qu'on ignore l'index du df (pas utile ici)
for _, row in df.iterrows():
    ## Liste des réponses possibles
    # on crée la liste choix pour les réponses possibles
    # on parcourt les colonnes "responseA" à "D" et on garde celles qui ne sont pas NaN
    choix = [row[c] for c in ["responseA", "responseB", "responseC", "responseD"] if pd.notna(row[c])]

    ## Liste des bonnes réponses (peut contenir 1 ou plusieurs lettres)
    # on récupère les lettres des bonnes réponses
    # re.split(..) découpe une chaîne en morceaux selon un motif
    # r"[,\s]+" = c'est le motif à chercher (, : virgule et \s : espace blanc) et + : peu importe combien il y en a
    # on transforme "A,C" ou "A C" en ["A", "C"]
    correct_letters = re.split(r"[,\s]+", str(row["correct"]).strip(","))
    # on initialise une liste vide pour stocker les textes des bonnes réponses
    bonnes_reponses = []

    # on parcourt chaque lettre 
    for letter in correct_letters:
        # .strip() enlève les espaces éventuels
        letter = letter.strip()
        # on vérifie que la lettre est bien dans index_map
        # et que l'indice ne dépasse pas la taille de choix
        if letter in index_map and index_map[letter] < len(choix):
            # on ajoute le texte de la bonne réponse dans la liste bonne_reponses
            bonnes_reponses.append(choix[index_map[letter]])


## Construction du dictionnaire final pour chaque question
    # on ajoute aussi les colonnes "subject", "use" et "remark"
    # row.get("...") essaie de récupérer la valeur de la colonne renseignée entre ()
    # si valeur manquante = ça renvoie None
    document = {
        "question": row["question"],
        "subject": row.get("subject", None),
        "use": row.get("use", None),
        "correct": bonnes_reponses,
        "responses": choix,
        "remark": row.get("remark", None)
    }

    # on ajoute ce dictionnaire à la liste documents
    documents.append(document)

df_clean= pd.DataFrame(documents)
#print (df_clean)

##### test
# row = df.iloc[42]  # par exemple la 45e question
# index_map = {"A": 0, "B": 1, "C": 2, "D": 3}
# choix = [row[c] for c in ["responseA", "responseB", "responseC", "responseD"] if pd.notna(row[c])]
# correct_letters = re.split(r"[,\s]+", str(row["correct"]).strip())
# bonnes_reponses = []

# for letter in correct_letters:
#     letter = letter.strip()
#     if letter in index_map and index_map[letter] < len(choix):
#         bonnes_reponses.append({
#                 "lettre": letter,
#                 "choix":choix[index_map[letter]]
#                 })

# print("Question :", row["question"])
# print("Réponses possibles :", choix)
# print("Lettres correctes :", correct_letters)
# print("Bonnes réponses :", bonnes_reponses)
# print("thème :",  row.get("subject"))
# print("niveau :", row.get("use"))
########



##### Gérer plusieurs questions avec le même intutilé

# on ajoute une colonne temporaire "question_clean"
# pour obtenir une version plus uniforme des questions
df_clean["question_clean"] = (
    df_clean["question"]        # on sélectionne la colonne question
    .str.strip()                # enlève les espaces
    .str.rstrip(":")            # enlève les ":" à la fin
    .str.replace(r"\s+", " ", regex=True)  # remplace les espaces multiples par un seul
)

# repérer les questions en plusieurs exemplaires dans le df_clean
questions_a_fusionner = (
    df_clean["question_clean"]  # on enlève les espaces en début/fin dans les intitulés
    .value_counts()             # on compte combien de fois chaque question apparaît
    .loc[lambda x: x > 1]       # on garde uniquement celles qui apparaissent plus d’une fois
    .index.tolist()             # on récupère la liste des intitulés concernés
)

# on initialise une liste pour les nouvelles lignes fusionnées
lignes_fusionnees = []          # une liste vide qui va contenir les nouvelles lignes fusionnées
masque_total = pd.Series(False, index=df_clean.index)   # masque booléen initialisé à False partout, qui servira à repérer les lignes à supprimer
# masque_total: on construit un masque booléen qui permettra de marquer les lignes à supprimer plus tard
# pd.Series(False, ...) : crée une série pandas remplie de False 
# (donc tous les éléments sont initialement à False)
# index=df_clean.index : on donne à cette série le même index que celui de df_clean
# à chaque tour de boucle, on mettra certains index à True pour les marquer comme “à supprimer”

# on boucle sur chaque question à fusionner
for question in questions_a_fusionner:
    # on extrait toutes les lignes du df_clean qui correspondent à cette question
    groupe = df_clean[df_clean["question_clean"] == question]
    
    # Fusion des réponses
    merged_responses = sum(groupe["responses"], [])
    
    # Fusion des bonnes réponses
    merged_correct = sum(groupe["correct"], [])
    
    # Création de la nouvelle ligne
    new_row = {
        "question": question,
        "subject": groupe.iloc[0].get("subject", "N/A"),
        "use": groupe.iloc[0].get("use", "fusionnée"),
        "correct": merged_correct,
        "responses": merged_responses,
        "remark": row.get("remark", None)
    }

    # on ajoute cette ligne à la liste des lignes fusionnées
    lignes_fusionnees.append(new_row)
    
    # Mise à jour du masque 
    # | met à True les lignes qui correspondent à la question en cours de fusion
    # pour les marquer comme “à supprimer”
    masque_total |= df_clean["question"].str.strip() == question.strip()


# on met à jour df_clean
# ~masque_total : on inverse le masque pour ne garder que les lignes qu’on n’a pas fusionnées
df_clean = df_clean[~masque_total]
# on transforme le liste "lignes_fusionnees" en df
# on concatène df_clean et le df avec les lignes fusionnées
# on réindexe df_clean final de façon propre, sans garder les anciens index
df_clean = pd.concat([df_clean, pd.DataFrame(lignes_fusionnees)], ignore_index=True)

# Suppression de la colonne temporaire
df_clean.drop(columns=["question_clean"], inplace=True)

# print(df_clean)

# on génère un fichier json prêt à être ajouter dans MongoDB
df_clean.to_json("questions.json", orient="records", force_ascii=False, indent=2)
# orient="records" : chaque ligne devient un objet JSON indépendant (format classique pour des listes de dictionnaires)
# force_ascii=False : permet de garder les accents et caractères spéciaux
# indent=2 : rend le fichier lisible et bien indenté










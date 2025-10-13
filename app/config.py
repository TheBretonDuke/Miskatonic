"""
Configuration et métadonnées de l'application FastAPI
"""

app_config = {
    "title": "Miskatonic Quiz API",
    "version": "1.0.0",
    "description": """
    ## API de Génération de Quiz - Miskatonic University

    Cette API permet aux enseignants de gérer des questions de quiz et de créer des évaluations personnalisées.

    ### Fonctionnalités principales :
    - **Authentification** : Gestion des utilisateurs avec rôles (étudiant/prof/admin)
    - **Questions** : CRUD complet avec filtrage par thème et test
    - **Quiz** : Génération aléatoire et validation des réponses
    - **Sécurité** : Contrôle d'accès basé sur les rôles

    ### Bases de données :
    - **MongoDB** : Stockage des questions et sessions de quiz
    - **SQLite** : Gestion des utilisateurs et authentification

    ### Utilisation :
    1. Créer un compte via `/register`
    2. Se connecter via `/login` 
    3. Accéder aux questions selon son rôle
    4. Générer et passer des quiz
    """,
    "contact": {
        "name": "Équipe Miskatonic Dev",
        "email": "dev@miskatonic.edu",
    },
    "license_info": {
        "name": "MIT License",
        "url": "https://opensource.org/licenses/MIT",
    },
    "openapi_tags": [
        {
            "name": "authentification",
            "description": "Opérations de connexion et création de compte",
        },
        {
            "name": "questions",
            "description": "Gestion des questions de quiz (CRUD)",
        },
        {
            "name": "quiz",
            "description": "Génération de quiz et validation des réponses",
        },
        {
            "name": "utilitaires",
            "description": "Endpoints d'aide (thèmes, tests disponibles)",
        },
    ]
}

cors_config = {
    "allow_origins": ["*"],
    "allow_credentials": True,
    "allow_methods": ["*"],
    "allow_headers": ["*"],
}
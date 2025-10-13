"""
Miskatonic Quiz API - Point d'entrée principal

API simple et bien organisée pour la gestion de quiz universitaires.
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from .config import app_config, cors_config
from .database import init_db
from .routes import auth_routes, questions_routes, quiz_routes, utilities_routes


# Initialisation de l'application
app = FastAPI(**app_config)
init_db()

# Configuration CORS
app.add_middleware(CORSMiddleware, **cors_config)

# Enregistrement des routes
app.include_router(auth_routes.router)
app.include_router(questions_routes.router)
app.include_router(quiz_routes.router)
app.include_router(utilities_routes.router)
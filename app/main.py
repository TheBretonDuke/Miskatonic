from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List

from app.database import init_db, create_user, authenticate_user
from app.questions import get_questions

# --- INITIALISATION ---
app = FastAPI()
init_db()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# --- MODELS ---
class Question(BaseModel):
    question: str
    theme: str
    niveau: str
    choix: List[str]
    correct: List[str]

class UserIn(BaseModel):
    username: str
    password: str
    role: str = "prof"  # 👈 rôle optionnel à l'inscription

class AnswerIn(BaseModel):
    username: str
    question: str
    reponse: List[str]

# --- ROUTES ---

@app.get("/questions", response_model=List[Question])
def get_questions_route(limit: int = 5):
    questions = get_questions(limit=limit)
    if not questions:
        raise HTTPException(status_code=500, detail="Aucune question disponible")
    return questions

@app.post("/register")
def register(user: UserIn):
    """Créer un nouvel utilisateur (stocké en SQLite)"""
    ok = create_user(user.username, user.password, user.role)
    if not ok:
        raise HTTPException(status_code=400, detail="Utilisateur déjà existant")
    return {"message": f"Utilisateur {user.username} créé avec succès (rôle={user.role})"}

@app.post("/login")
def login(user: UserIn):
    """Authentifier un utilisateur (SQLite)"""
    ok, role = authenticate_user(user.username, user.password)
    if ok:
        return {"message": "Connexion réussie", "role": role}
    raise HTTPException(status_code=401, detail="Identifiants invalides")

@app.post("/answer")
def answer(ans: AnswerIn):
    from app.questions import collection
    q = collection.find_one({"question": ans.question})
    if not q:
        raise HTTPException(status_code=404, detail="Question inconnue")

    is_correct = (set(ans.reponse) == set(q.get("correct", [])))
    return {"correct": is_correct}

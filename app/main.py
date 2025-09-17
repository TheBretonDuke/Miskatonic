from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app import questions

app = FastAPI()

# Autoriser les requêtes depuis ton frontend local
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tu peux restreindre à ["http://127.0.0.1:5500"] si tu utilises Live Server
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Inclure routes questions
app.include_router(questions.router, prefix="/questions", tags=["questions"])

@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API Quiz"}

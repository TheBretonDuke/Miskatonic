from fastapi import FastAPI
from app import questions   # import du fichier questions.py

app = FastAPI()

# On inclut le routeur "questions"
app.include_router(questions.router, prefix="/questions", tags=["questions"])

@app.get("/")
def root():
    return {"message": "Bienvenue sur l'API Quiz"}

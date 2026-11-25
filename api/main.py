from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from . import models
from .core.database import Base, engine
from .routers import hangman, players


Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Atividade Final - Mini Jogo de Forca via API",
    description=(
        "Implementação do Jogo da Forca com FastAPI e SQLite "
        "para a disciplina de Desenvolvimento Rápido."
    ),
    version="1.0.0",
)

origins = [
    "http://127.0.0.1:8000",
    "http://localhost:8000",
    "http://127.0.0.1:5500",
    "http://localhost:5500",
    "*",
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(players.router, tags=["Jogadores"])
app.include_router(hangman.router, tags=["Forca"])


@app.get("/")
def read_root():
    return {
        "message": "API do Jogo da Forca rodando. Acesse /docs para ver os endpoints."
    }

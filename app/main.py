# app/main.py

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import engine, Base
from .routers import hangman

# Cria as tabelas no SQLite se elas ainda não existirem
Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Atividade Final - Mini Jogo de Forca via API",
    description="Implementação do Jogo da Forca com FastAPI e SQLite para a disciplina de Desenvolvimento Rápido.",
    version="1.0.0"
)

# =================================================================
# CONFIGURAÇÃO DO MIDDLEWARE CORS (Correção para o frontend)
# =================================================================
origins = [
    # A ORIGEM ONDE O FASTAPI ESTÁ RODANDO (API)
    "http://127.0.0.1:8000",
    "http://localhost:8000",

    # A ORIGEM EXATA ONDE O SEU LIVE SERVER ESTÁ RODANDO (FRONTEND)
    "http://127.0.0.1:5500",  # <--- Adicione a porta 5500 se for essa!
    "http://localhost:5500",  # <--- Adicione o localhost:5500 se for essa!

    # Manter o curinga é opcional, mas vamos focar nas URLs específicas
     "*"
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,  # Use a lista específica AGORA
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
# =================================================================

# Inclui as rotas do jogo no app principal
app.include_router(hangman.router, tags=["Forca e Jogadores"])

# Rota de teste
@app.get("/")
def read_root():
    return {"message": "API do Jogo da Forca rodando. Acesse /docs para ver os endpoints."}
# app/database.py

import sqlite3
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Cria o arquivo SQLite no diretório raiz do projeto
# O "check_same_thread=False" é necessário para o SQLite
# rodar de forma assíncrona com o FastAPI/SQLAlchemy
SQLALCHEMY_DATABASE_URL = "sqlite:///./hangman_game.db"

# O motor de conexão com o DB
engine = create_engine(
    SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False}
)

# A classe SessionLocal é o que usaremos para criar uma session do DB
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Base para a declaração dos modelos (tabelas)
Base = declarative_base()

# Função de utilidade para obter a sessão do DB no FastAPI
def get_db():
    """Dependência que garante que a conexão é fechada após o uso."""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
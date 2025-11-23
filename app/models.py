# app/models.py

from sqlalchemy import Column, Integer, String, Boolean, ForeignKey
from sqlalchemy.orm import relationship
from pydantic import BaseModel
from typing import List, Optional

from .database import Base


# --- Modelos SQLAlchemy (Mapeamento do Banco de Dados) ---

class Player(Base):
    """Tabela para armazenar os jogadores."""
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    # Relação com a tabela Game
    games = relationship("Game", back_populates="player")


class Game(Base):
    """Tabela para armazenar as partidas de Forca."""
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    word = Column(String)  # Palavra secreta
    guessed_letters = Column(String, default="")  # Letras tentadas (separadas por vírgula)
    attempts_left = Column(Integer)
    status = Column(String, default="IN_PROGRESS")  # IN_PROGRESS, WIN, LOSE

    # Relação com a tabela Player
    player = relationship("Player", back_populates="games")


# --- Modelos Pydantic (Schema para API) ---

# 1. POST /players (Entrada)
class PlayerCreate(BaseModel):
    name: str


# 1. POST /players (Saída) ou /players/{id}
class PlayerSchema(BaseModel):
    id: int
    name: str

    class Config:
        from_attributes = True


# 2. POST /hangman/start (Entrada)
class GameStart(BaseModel):
    player_id: int


# 3. POST /hangman/guess (Entrada)
class GameGuess(BaseModel):
    game_id: int
    letter: str


# 4. GET /hangman/status/{game_id} e Saída do /guess
class GameStatus(BaseModel):
    game_id: int
    masked_word: str
    attempts_left: int
    status: str
    hit: Optional[bool] = None  # Campo opcional, útil na resposta do /guess
    guessed_letters: Optional[str] = None

    class Config:
        from_attributes = True


# 5. GET /hangman/scoreboard (Saída)
class ScoreboardEntry(BaseModel):
    player_id: int
    name: str
    wins: int
    losses: int
    total_games: int
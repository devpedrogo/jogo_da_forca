from typing import Optional

from pydantic import BaseModel


class GameStart(BaseModel):
    player_id: int


class GameGuess(BaseModel):
    game_id: int
    letter: str


class GameStatus(BaseModel):
    game_id: int
    masked_word: str
    attempts_left: int
    status: str
    hit: Optional[bool] = None
    guessed_letters: Optional[str] = None


class ScoreboardEntry(BaseModel):
    player_id: int
    name: str
    wins: int
    losses: int
    total_games: int

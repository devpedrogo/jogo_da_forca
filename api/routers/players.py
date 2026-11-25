from typing import List

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..schemas import PlayerCreate, PlayerSchema, ScoreboardEntry
from ..services import player_service
from ..services.exceptions import PlayerAlreadyExists


router = APIRouter()


@router.post(
    "/players",
    response_model=PlayerSchema,
    status_code=status.HTTP_201_CREATED,
)
def create_player_endpoint(
    player: PlayerCreate,
    db: Session = Depends(get_db),
):
    try:
        return player_service.create_player(db, player.name)
    except PlayerAlreadyExists:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail={"error": "Jogador já existe.", "code": 409},
        )


@router.get("/players/{player_name}", response_model=PlayerSchema)
def read_player_by_name(player_name: str, db: Session = Depends(get_db)):
    player = player_service.get_player_by_name(db, player_name)
    if player is None:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")
    return player


@router.get(
    "/hangman/scoreboard",
    response_model=List[ScoreboardEntry],
)
def get_scoreboard_endpoint(db: Session = Depends(get_db)):
    return player_service.get_scoreboard(db)

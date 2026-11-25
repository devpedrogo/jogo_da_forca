from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from ..core.database import get_db
from ..schemas import GameGuess, GameStart, GameStatus
from ..services import game_service
from ..services.exceptions import (
    GameAlreadyFinished,
    GameNotFound,
    InvalidGuess,
    PlayerNotFound,
)


router = APIRouter()


def _to_game_status(game, hit=None):
    return GameStatus(
        game_id=game.id,
        masked_word=game_service.get_masked_word(
            game.word,
            game.guessed_letters,
        ),
        attempts_left=game.attempts_left,
        status=game.status,
        hit=hit,
        guessed_letters=game.guessed_letters.replace(",", ", "),
    )


@router.post("/hangman/start", response_model=GameStatus)
def start_game_endpoint(
    game_data: GameStart,
    db: Session = Depends(get_db),
):
    try:
        game = game_service.start_game(db, game_data.player_id)
    except PlayerNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Jogador não encontrado", "code": 404},
        )
    return _to_game_status(game)


@router.post("/hangman/guess", response_model=GameStatus)
def make_guess_endpoint(
    guess: GameGuess,
    db: Session = Depends(get_db),
):
    try:
        game, hit = game_service.make_guess(db, guess.game_id, guess.letter)
    except GameNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Jogo não encontrado", "code": 404},
        )
    except GameAlreadyFinished as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={
                "error": f"O jogo {error}. Não é possível jogar.",
                "code": 400,
            },
        )
    except InvalidGuess as error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": str(error), "code": 400},
        )
    return _to_game_status(game, hit=hit)


@router.get("/hangman/status/{game_id}", response_model=GameStatus)
def get_game_status_endpoint(
    game_id: int,
    db: Session = Depends(get_db),
):
    try:
        game = game_service.get_game(db, game_id)
    except GameNotFound:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Jogo não encontrado", "code": 404},
        )
    return _to_game_status(game)

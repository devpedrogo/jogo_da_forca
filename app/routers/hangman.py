# app/routers/hangman.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from .. import crud, models
from ..database import get_db
from typing import List

router = APIRouter()


# 1. POST /players
@router.post("/players", response_model=models.PlayerSchema, status_code=status.HTTP_201_CREATED)
def create_player_endpoint(player: models.PlayerCreate, db: Session = Depends(get_db)):
    """Cria um novo jogador."""
    # O modelo PlayerCreate garante que temos o campo 'name'
    return crud.create_player(db, player.name)


# 2. POST /hangman/start
@router.post("/hangman/start", response_model=models.GameStatus)
def start_game_endpoint(game_data: models.GameStart, db: Session = Depends(get_db)):
    """Inicia uma nova partida de Forca para um jogador."""

    # 1. Verifica se o jogador existe (Requisito 404)
    if not crud.get_player(db, game_data.player_id):
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Jogador não encontrado", "code": 404}
        )

    # 2. Cria o jogo no DB
    db_game = crud.start_new_game(db, game_data.player_id)

    # 3. Retorna o status inicial
    return models.GameStatus(
        game_id=db_game.id,
        masked_word=crud.get_masked_word(db_game.word, db_game.guessed_letters),
        attempts_left=db_game.attempts_left,
        status=db_game.status,
        guessed_letters = db_game.guessed_letters.replace(',', ', ')
    )


# 3. POST /hangman/guess
@router.post("/hangman/guess", response_model=models.GameStatus)
def make_guess_endpoint(guess: models.GameGuess, db: Session = Depends(get_db)):
    """Recebe uma letra e processa a jogada."""

    db_game = crud.get_game(db, guess.game_id)

    # 1. Verifica se o jogo existe (Requisito 404)
    if not db_game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Jogo não encontrado", "code": 404}
        )

    # 2. Verifica se a partida já terminou
    if db_game.status != "IN_PROGRESS":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": f"O jogo {db_game.status}. Não é possível jogar.", "code": 400}
        )

    letter = guess.letter.upper()

    # 3. Validação da letra (Requisito 400 - jogada inválida)
    if not letter.isalpha() or len(letter) != 1:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": "A jogada deve ser uma única letra do alfabeto.", "code": 400}
        )

    # Verifica se já tentou a letra
    if letter in db_game.guessed_letters.split(','):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"error": f"A letra '{letter}' já foi tentada.", "code": 400}
        )

    # 4. Processa a jogada
    hit = crud.make_guess(db, db_game, letter)

    # 5. Retorna o status atualizado
    return models.GameStatus(
        game_id=db_game.id,
        masked_word=crud.get_masked_word(db_game.word, db_game.guessed_letters),
        attempts_left=db_game.attempts_left,
        status=db_game.status,
        hit=hit,  # Adiciona a informação se acertou ou errou
        guessed_letters = db_game.guessed_letters.replace(',', ', ')
    )


# 4. GET /hangman/status/{game_id}
@router.get("/hangman/status/{game_id}", response_model=models.GameStatus)
def get_game_status_endpoint(game_id: int, db: Session = Depends(get_db)):
    """Retorna o estado atual da partida."""

    db_game = crud.get_game(db, game_id)

    if not db_game:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail={"error": "Jogo não encontrado", "code": 404}
        )

    # Retorna o status
    return models.GameStatus(
        game_id=db_game.id,
        masked_word=crud.get_masked_word(db_game.word, db_game.guessed_letters),
        attempts_left=db_game.attempts_left,
        status=db_game.status,
        guessed_letters=db_game.guessed_letters.replace(',', ', ')
    )


# 5. GET /hangman/scoreboard
@router.get("/hangman/scoreboard", response_model=List[models.ScoreboardEntry])
def get_scoreboard_endpoint(db: Session = Depends(get_db)):
    """Retorna o placar de vitórias/derrotas por jogador."""
    return crud.get_scoreboard(db)


# NOVO ENDPOINT: Busca jogador pelo nome
@router.get("/players/{player_name}", response_model=models.PlayerSchema)
def read_player_by_name(player_name: str, db: Session = Depends(get_db)):
    """Busca um jogador pelo nome."""
    db_player = crud.get_player_by_name(db, player_name)

    # [cite_start]Tratamento de Erro: 404 - Jogador não encontrado [cite: 170]
    if db_player is None:
        raise HTTPException(status_code=404, detail="Jogador não encontrado")

    return db_player
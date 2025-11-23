# app/crud.py

from sqlalchemy.orm import Session, joinedload # CORREÇÃO: joinedload importado diretamente
from . import models
from .models import Player, Game
from typing import List
import random
import os

# Palavra e tentativas são fixas, mas o ideal seria usar .env ou DB
DEFAULT_WORD_LIST = ["FASTAPI", "PYTHON", "HANGMAN", "APIREST", "LOCK"]
MAX_ATTEMPTS = 6


# --- Funções para Player (Jogador) ---

def create_player(db: Session, player_name: str):
    """Cria um novo jogador na base de dados."""
    db_player = Player(name=player_name)
    db.add(db_player)
    db.commit()
    db.refresh(db_player)
    return db_player


def get_player(db: Session, player_id: int):
    """Busca um jogador pelo ID."""
    return db.query(Player).filter(Player.id == player_id).first()

def get_player_by_name(db: Session, player_name: str):
    """Busca um jogador pelo nome."""
    # O .first() retorna o objeto Player ou None se não encontrar
    return db.query(Player).filter(Player.name == player_name).first()

# --- Funções para Game (Partida de Forca) ---

def start_new_game(db: Session, player_id: int):
    """Inicia uma nova partida de Forca."""
    # 1. Sorteia a palavra
    word_to_guess = random.choice(DEFAULT_WORD_LIST).upper()

    # 2. Cria o registro no DB
    db_game = Game(
        player_id=player_id,
        word=word_to_guess,
        attempts_left=MAX_ATTEMPTS,
        status="IN_PROGRESS"
    )
    db.add(db_game)
    db.commit()
    db.refresh(db_game)
    return db_game


def get_game(db: Session, game_id: int):
    """Busca um jogo pelo ID."""
    return db.query(Game).filter(Game.id == game_id).first()


def get_masked_word(word: str, guessed_letters: str) -> str:
    """Retorna a palavra com as letras não descobertas como '_'. (Ex: C_RR_)."""
    masked = "".join([
        letter if letter in guessed_letters else "_"
        for letter in word
    ])
    return masked


def update_game_status(db: Session, db_game: Game):
    """Verifica e atualiza o status do jogo (WIN/LOSE)."""
    masked = get_masked_word(db_game.word, db_game.guessed_letters)

    if "_" not in masked:
        db_game.status = "WIN"
    elif db_game.attempts_left <= 0:
        db_game.status = "LOSE"

    db.commit()
    db.refresh(db_game)
    return db_game


def make_guess(db: Session, db_game: Game, letter: str) -> bool:
    """Tenta uma letra e atualiza o estado do jogo. Retorna True se acertou."""

    letter = letter.upper()
    hit = False

    # 1. Verifica se já tentou essa letra
    if letter in db_game.guessed_letters:
        # Não muda nada, mas a jogada deve ser considerada inválida no router (400)
        return False

        # 2. Adiciona a letra às tentadas
    if db_game.guessed_letters:
        db_game.guessed_letters += f",{letter}"
    else:
        db_game.guessed_letters = letter

    # 3. Verifica se a letra está na palavra
    if letter in db_game.word:
        hit = True
    else:
        # Se errou, decrementa tentativas
        db_game.attempts_left -= 1

    # 4. Atualiza o status de WIN/LOSE
    update_game_status(db, db_game)

    return hit


def get_scoreboard(db: Session) -> List[models.ScoreboardEntry]:
    """Calcula e retorna o placar de vitórias/derrotas por jogador."""

    # Consulta todos os jogadores e seus jogos
    players_with_games = db.query(Player).options(
        # CORREÇÃO: Chama joinedload diretamente, pois foi importado no topo
        joinedload(Player.games)
    ).all()

    scoreboard = []

    for player in players_with_games:
        wins = sum(1 for game in player.games if game.status == "WIN")
        losses = sum(1 for game in player.games if game.status == "LOSE")
        total_games = len(player.games)

        scoreboard.append(models.ScoreboardEntry(
            player_id=player.id,
            name=player.name,
            wins=wins,
            losses=losses,
            total_games=total_games
        ))

    return scoreboard
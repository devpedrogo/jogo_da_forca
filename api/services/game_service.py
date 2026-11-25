import random

from sqlalchemy.orm import Session

from .. import repositories
from ..models import Game
from .exceptions import (
    GameAlreadyFinished,
    GameNotFound,
    InvalidGuess,
    PlayerNotFound,
)


DEFAULT_WORD_LIST = ["FASTAPI", "PYTHON", "HANGMAN", "APIREST", "LOCK"]
MAX_ATTEMPTS = 6


def get_masked_word(word: str, guessed_letters: str) -> str:
    """Oculta as letras ainda não tentadas, preservando as já descobertas."""
    return "".join(
        letter if letter in guessed_letters else "_" for letter in word
    )


def start_game(db: Session, player_id: int) -> Game:
    """Valida o jogador e persiste uma nova partida com palavra aleatória."""
    if not repositories.player_repository.get_by_id(db, player_id):
        raise PlayerNotFound

    word = random.choice(DEFAULT_WORD_LIST).upper()
    return repositories.game_repository.create(
        db,
        player_id=player_id,
        word=word,
        attempts=MAX_ATTEMPTS,
    )


def get_game(db: Session, game_id: int) -> Game:
    """Retorna uma partida existente ou sinaliza que ela não foi encontrada."""
    game = repositories.game_repository.get_by_id(db, game_id)
    if game is None:
        raise GameNotFound
    return game


def make_guess(db: Session, game_id: int, letter: str):
    """Valida e aplica uma tentativa, atualiza o estado e persiste a partida.

    Retorna a partida atualizada e um booleano que indica se a letra acertou.
    """
    game = get_game(db, game_id)
    if game.status != "IN_PROGRESS":
        raise GameAlreadyFinished(game.status)

    letter = letter.upper()
    if len(letter) != 1 or not letter.isalpha():
        raise InvalidGuess("A jogada deve ser uma única letra do alfabeto.")
    if letter in game.guessed_letters.split(","):
        raise InvalidGuess(f"A letra '{letter}' já foi tentada.")

    game.guessed_letters = (
        f"{game.guessed_letters},{letter}"
        if game.guessed_letters
        else letter
    )
    hit = letter in game.word
    if not hit:
        game.attempts_left -= 1

    masked_word = get_masked_word(game.word, game.guessed_letters)
    if "_" not in masked_word:
        game.status = "WIN"
    elif game.attempts_left <= 0:
        game.status = "LOSE"

    repositories.game_repository.save(db, game)
    return game, hit

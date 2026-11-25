from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from .. import repositories
from ..schemas.game import ScoreboardEntry
from .exceptions import PlayerAlreadyExists


def create_player(db: Session, name: str):
    """Cria um jogador e converte violações de unicidade em erro de domínio."""
    try:
        return repositories.player_repository.create(db, name)
    except IntegrityError as error:
        db.rollback()
        raise PlayerAlreadyExists from error


def get_player(db: Session, player_id: int):
    """Busca um jogador pelo identificador ou retorna None se não existir."""
    return repositories.player_repository.get_by_id(db, player_id)


def get_player_by_name(db: Session, name: str):
    """Busca um jogador pelo nome exato ou retorna None se não existir."""
    return repositories.player_repository.get_by_name(db, name)


def get_scoreboard(db: Session):
    """Monta o placar com vitórias, derrotas e total de partidas por jogador."""
    scoreboard = []
    players = repositories.player_repository.list_with_games(db)

    for player in players:
        wins = sum(1 for game in player.games if game.status == "WIN")
        losses = sum(1 for game in player.games if game.status == "LOSE")
        scoreboard.append(
            ScoreboardEntry(
                player_id=player.id,
                name=player.name,
                wins=wins,
                losses=losses,
                total_games=len(player.games),
            )
        )

    return scoreboard

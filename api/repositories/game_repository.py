from sqlalchemy.orm import Session

from ..models import Game


def create(db: Session, player_id: int, word: str, attempts: int) -> Game:
    game = Game(
        player_id=player_id,
        word=word,
        attempts_left=attempts,
        status="IN_PROGRESS",
    )
    db.add(game)
    db.commit()
    db.refresh(game)
    return game


def get_by_id(db: Session, game_id: int):
    return db.query(Game).filter(Game.id == game_id).first()


def save(db: Session, game: Game) -> Game:
    db.commit()
    db.refresh(game)
    return game

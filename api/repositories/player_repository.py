from sqlalchemy.orm import Session, joinedload

from ..models import Player


def create(db: Session, name: str) -> Player:
    player = Player(name=name)
    db.add(player)
    db.commit()
    db.refresh(player)
    return player


def get_by_id(db: Session, player_id: int):
    return db.query(Player).filter(Player.id == player_id).first()


def get_by_name(db: Session, name: str):
    return db.query(Player).filter(Player.name == name).first()


def list_with_games(db: Session):
    return db.query(Player).options(joinedload(Player.games)).all()

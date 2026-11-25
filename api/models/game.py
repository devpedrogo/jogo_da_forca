from sqlalchemy import Column, ForeignKey, Integer, String
from sqlalchemy.orm import relationship

from ..core.database import Base


class Game(Base):
    __tablename__ = "games"

    id = Column(Integer, primary_key=True, index=True)
    player_id = Column(Integer, ForeignKey("players.id"))
    word = Column(String)
    guessed_letters = Column(String, default="")
    attempts_left = Column(Integer)
    status = Column(String, default="IN_PROGRESS")

    player = relationship("Player", back_populates="games")

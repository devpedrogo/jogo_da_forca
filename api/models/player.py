from sqlalchemy import Column, Integer, String
from sqlalchemy.orm import relationship

from ..core.database import Base


class Player(Base):
    __tablename__ = "players"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)

    games = relationship("Game", back_populates="player")

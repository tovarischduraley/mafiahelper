import datetime
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column

Base = declarative_base()


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    fio: Mapped[Optional[str]] = mapped_column(nullable=True)
    nickname: Mapped[Optional[str]] = mapped_column(nullable=True)


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True)
    result: Mapped[str] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(nullable=False)
    comments: Mapped[str] = mapped_column(nullable=False, default="")
    created_at: Mapped[datetime.datetime] = mapped_column(nullable=False)


class UsersGames(Base):
    __tablename__ = "users_games"
    user_id: Mapped[int] = mapped_column(ForeignKey('users.id'), primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey('games.id'), primary_key=True)
    role: Mapped[str] = mapped_column(nullable=False)
    number: Mapped[int] = mapped_column(nullable=False)

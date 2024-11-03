import datetime
from typing import Optional

from sqlalchemy import ForeignKey
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship


class Base(DeclarativeBase): ...


class UserGame(Base):
    __tablename__ = "users_games"
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"), primary_key=True)
    game_id: Mapped[int] = mapped_column(ForeignKey("games.id"), primary_key=True)
    role: Mapped[str] = mapped_column(nullable=False)
    number: Mapped[int] = mapped_column(nullable=False)

    player: Mapped["User"] = relationship(back_populates="games")
    game: Mapped["Game"] = relationship(back_populates="players")

    def __repr__(self) -> str:
        return (
            f"<UserGame "
            f"user_id={self.user_id} "
            f"game_id={self.game_id} "
            f"role={self.role} "
            f"number={self.number} "
        )


class User(Base):
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    fio: Mapped[Optional[str]] = mapped_column(nullable=True)
    nickname: Mapped[Optional[str]] = mapped_column(nullable=True)

    games: Mapped[list["UserGame"]] = relationship(back_populates="player")

    def __repr__(self) -> str:
        return f"<User id={self.id} nickname={self.nickname}>"


class Game(Base):
    __tablename__ = "games"

    id: Mapped[int] = mapped_column(primary_key=True)
    result: Mapped[str] = mapped_column(nullable=True)
    status: Mapped[str] = mapped_column(nullable=False)
    comments: Mapped[str] = mapped_column(nullable=False, default="")
    created_at: Mapped[datetime.datetime] = mapped_column(nullable=False)

    players: Mapped[list["UserGame"]] = relationship(back_populates="game")

    def __repr__(self) -> str:
        return f"<Game id={self.id} created_at={self.created_at}>"

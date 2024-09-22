from typing import Optional

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import Mapped, mapped_column

Base = declarative_base()

class User(Base):
    __tablename__ = 'users'

    id: Mapped[int] = mapped_column(primary_key=True)
    fio: Mapped[Optional[str]] = mapped_column(nullable=True)
    nickname: Mapped[Optional[str]] = mapped_column(nullable=True)


class Game(Base):
    __tablename__ = 'games'

    id: Mapped[int] = mapped_column(primary_key=True)
    result: Mapped[str] = mapped_column(nullable=False)


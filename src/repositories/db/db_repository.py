from typing import Self

from sqlalchemy import select
from sqlalchemy.ext.asyncio import async_sessionmaker

from usecases.interfaces import DBRepositoryInterface
from usecases.schemas import CreateGameSchema, CreateUserSchema, UpdateGameSchema, UserSchema

from .models import User


class DBRepository(DBRepositoryInterface):
    def __init__(self, session_factory: async_sessionmaker) -> None:
        self._session_maker = session_factory

    async def __aenter__(self) -> Self:
        self._session = self._session_maker()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        await self._session.close()

    async def create_user(self, user: CreateUserSchema) -> None:
        new_user = User(fio=user.fio, nickname=user.nickname)
        self._session.add(new_user)
        await self._session.commit()

    async def get_users(self, fio_or_nickname__in: str | None) -> list[UserSchema]:
        query = select(User)
        if fio_or_nickname__in is not None:
            query = query.where(User.fio.in_(fio_or_nickname__in))
        raw_users = await self._session.execute(query)
        return [UserSchema.model_validate(u, from_attributes=True) for u in raw_users]

    async def update_game(self, data: UpdateGameSchema) -> None:
        ...

    async def create_game(self, data: CreateGameSchema) -> None:
        pass

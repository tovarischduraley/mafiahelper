from typing import Self

from usecases.interfaces import DBRepositoryInterface
from usecases.schemas import CreateGameSchema, UpdateGameSchema, UserSchema, CreateUserSchema


class DBRepository(DBRepositoryInterface):
    async def __aenter__(self) -> Self:
        pass

    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None:
        pass

    async def create_user(self, user: CreateUserSchema) -> None:
        pass

    async def get_users(self, fio_or_nickname__in: str | None) -> list[UserSchema]:
        pass

    async def update_game(self, data: UpdateGameSchema) -> None:
        pass

    async def create_game(self, data: CreateGameSchema) -> None:
        pass

    def __init__(self) -> None: ...

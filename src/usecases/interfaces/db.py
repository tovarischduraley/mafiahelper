from abc import ABC, abstractmethod
from typing import Self

from usecases.schemas import CreateGameSchema, CreateUserSchema, GameSchema, UpdateGameSchema, UserSchema
from usecases.schemas.games import RawGameSchema


class DBRepositoryInterface(ABC):
    @abstractmethod
    async def __aenter__(self) -> Self: ...

    @abstractmethod
    async def __aexit__(self, exc_type, exc_val, exc_tb) -> None: ...

    @abstractmethod
    async def create_user(self, user: CreateUserSchema) -> None: ...

    @abstractmethod
    async def get_users(
        self,
        fio_or_nickname__ilike: str | None,
        limit: int | None,
        offset: int | None,
    ) -> list[UserSchema]: ...

    @abstractmethod
    async def get_user_by_id(self) -> UserSchema:
        ...

    @abstractmethod
    async def update_game(self, game_id: int, data: UpdateGameSchema) -> None: ...

    @abstractmethod
    async def create_game(self, data: CreateGameSchema) -> RawGameSchema: ...

    @abstractmethod
    async def get_game_by_id(self, game_id: int) -> GameSchema: ...

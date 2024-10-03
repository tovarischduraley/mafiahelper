from abc import ABC, abstractmethod

from usecases.schemas import CreatePlayerSchema, UpdateGameSchema, CreateGameSchema


class DBRepositoryInterface(ABC):
    @abstractmethod
    async def create_player(self, player: CreatePlayerSchema) -> None:
        ...

    @abstractmethod
    async def update_game(self, data: UpdateGameSchema) -> None:
        ...

    @abstractmethod
    async def create_game(self, data: CreateGameSchema) -> None:
        ...

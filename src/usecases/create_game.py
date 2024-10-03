from usecases.interfaces import DBRepositoryInterface
from usecases.schemas.games import CreateGameSchema


class CreateGameUseCase:
    def __init__(self, db: DBRepositoryInterface) -> None:
        self._db = db

    async def create_game(self, data: CreateGameSchema) -> None:
        await self._db.create_game(data)

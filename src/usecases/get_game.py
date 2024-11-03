from usecases.interfaces import DBRepositoryInterface
from usecases.schemas import GameSchema


class GetGameUseCase:
    def __init__(self, db: DBRepositoryInterface) -> None:
        self._db = db

    async def get_game(self, game_id: int) -> GameSchema:
        async with self._db as db:
            return await db.get_game_by_id(game_id)

import datetime

import core
from usecases.interfaces import DBRepositoryInterface
from usecases.schemas import CreateGameSchema, GameSchema


class CreateGameUseCase:
    def __init__(self, db: DBRepositoryInterface) -> None:
        self._db = db

    async def create_game_in_draft(self, created_at: datetime.datetime) -> GameSchema:
        async with self._db as db:
            raw_game = await db.create_game(
                CreateGameSchema(
                    players=[],
                    status=core.GameStatuses.DRAFT,
                    result=None,
                    comments="",
                    created_at=created_at,
                )
            )
            return await db.get_game_by_id(raw_game.id)

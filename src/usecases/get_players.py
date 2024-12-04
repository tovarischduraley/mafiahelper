from usecases.interfaces import DBRepositoryInterface
from usecases.schemas import PlayerSchema


class GetPlayersUseCase:
    def __init__(self, db: DBRepositoryInterface) -> None:
        self._db = db

    async def get_players(
        self,
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[PlayerSchema]:
        async with self._db as db:
            return await db.get_players(
                limit=limit,
                offset=offset,
            )

    async def get_players_count(self) -> int:
        async with self._db as db:
            return await db.get_players_count()

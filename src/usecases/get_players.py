from collections.abc import Iterable

from usecases.interfaces import DBRepositoryInterface
from usecases.schemas import PlayerSchema


class GetPlayersUseCase:
    def __init__(self, db: DBRepositoryInterface) -> None:
        self._db = db

    async def get_players(
        self,
        limit: int | None = None,
        offset: int | None = None,
    ) -> tuple[Iterable[PlayerSchema], int]:
        async with self._db as db:
            players = await db.get_players(
                limit=limit,
                offset=offset,
            )
            count = await db.get_players_count()
            return players, count

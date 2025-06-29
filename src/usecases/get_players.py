from collections.abc import Iterable

from core import GameStatuses
from usecases.interfaces import DBRepositoryInterface
from usecases.schemas import PlayerInGameSchema, PlayerSchema


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

    async def get_players_for_stream(self) -> set[PlayerInGameSchema] | None:
        async with self._db as db:
            games = await db.get_games(status=GameStatuses.DRAFT)
            if not games:
                return None
            return sorted(games, key=lambda g: g.created_at)[-1].players

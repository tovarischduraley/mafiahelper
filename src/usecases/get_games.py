from collections.abc import Iterable

from core import GameStatuses
from usecases.interfaces import DBRepositoryInterface
from usecases.schemas import GameSchema


class GetGamesUseCase:
    def __init__(self, db: DBRepositoryInterface) -> None:
        self._db = db

    async def get_game(self, game_id: int) -> GameSchema:
        async with self._db as db:
            return await db.get_game_by_id(game_id)

    async def get_ended_games(
        self,
        limit: int | None = None,
        offset: int | None = None,
    ) -> tuple[Iterable[GameSchema], int]:
        async with self._db as db:
            games = await db.get_games(
                status=GameStatuses.ENDED,
            )
            count = await db.get_ended_games_count()
            match limit, offset:
                case None, None:
                    ...
                case _, None:
                    games = games[:limit]
                case None, _:
                    games = games[offset:]
                case _, _:
                    games = games[offset:limit + offset]
            return games, count

    async def get_last_game_in_draft(self) -> GameSchema | None:
        async with self._db as db:
            games = await db.get_games(status=GameStatuses.DRAFT)
            if not games:
                return None
            return sorted(games, key=lambda g: g.created_at)[-1]

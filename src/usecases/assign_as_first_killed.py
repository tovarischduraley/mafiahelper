from usecases.interfaces.db import DBRepositoryInterface


class AssignAsFirstKilledUseCase:
    def __init__(self, db_repository: DBRepositoryInterface):
        self._db_repository = db_repository

    async def assign_player_as_first_killed(self, game_id: int, player_number: int) -> None:
        async with self._db_repository as db:
            # Check if player exists. raises NotFoundError
            _ = await self._db_repository.get_player_by_number(game_id=game_id, player_number=player_number)
            await db.assign_player_as_first_killed(game_id=game_id, player_number=player_number)

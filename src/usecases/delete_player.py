from usecases.errors import ValidationError
from usecases.interfaces import DBRepositoryInterface


class DeletePlayerUseCase:
    def __init__(self, db_repository: DBRepositoryInterface) -> None:
        self._db = db_repository

    async def delete_player(self, player_id: int) -> None:
        async with self._db as db:
            player_games = await db.get_games(player_id=player_id)
            if player_games:
               raise ValidationError("Could not delete player who participated in games")
            await db.delete_player(player_id=player_id)

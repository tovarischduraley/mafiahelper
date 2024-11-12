import core
from usecases.interfaces import DBRepositoryInterface
from usecases.schemas import GameSchema


class AssignPlayerToSeatUseCase:
    def __init__(self, db: DBRepositoryInterface) -> None:
        self._db = db

    async def assign_player_to_seat(
        self,
        game_id: int,
        player_id: int,
        seat_number: int,
        role: core.Roles,
    ) -> GameSchema:
        async with self._db as db:
            await db.remove_player(game_id, player_id)
            await db.remove_player_on_seat(game_id, seat_number=seat_number)
            await db.add_player(
                game_id=game_id,
                user_id=player_id,
                seat_number=seat_number,
                role=role,
            )
            return await self._db.get_game_by_id(game_id=game_id)

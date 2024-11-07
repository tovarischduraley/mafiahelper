import core
from bot.routes.users import players
from usecases.interfaces import DBRepositoryInterface


class AssignPlayerToSeatUseCase:
    def __init__(self, db: DBRepositoryInterface) -> None:
        self._db = db

    # async def assign_player_to_seat(self, game_id: int, player_id: int, number: int, role: core.Roles) -> None:
    #     async with self._db as db:
    #         player = await db.get_user_by_id(player_id)
    #         db.update_game(game_id=game_id)

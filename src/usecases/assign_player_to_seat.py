import core
from usecases.errors import ValidationError
from usecases.interfaces import DBRepositoryInterface
from usecases.schemas import GameSchema


class AssignPlayerToSeatUseCase:
    def __init__(self, db: DBRepositoryInterface) -> None:
        self._db = db

    @staticmethod
    def _validate_seat_number(seat_number: int) -> None:
        if not isinstance(seat_number, int):
            raise ValidationError(f"Seat number <{seat_number}> type is invalid. Expected <int>")
        if not 0 < seat_number < 11:
            raise ValidationError(f"Seat number <{seat_number}> is invalid. Expected 0 < seat < 11")

    async def assign_player_to_seat(
        self,
        game_id: int,
        player_id: int,
        seat_number: int,
        role: core.Roles,
    ) -> GameSchema:
        self._validate_seat_number(seat_number=seat_number)
        async with self._db as db:
            await db.remove_player_from_game(game_id, player_id)
            await db.remove_player_on_seat(game_id, seat_number=seat_number)
            await db.add_player(
                game_id=game_id,
                player_id=player_id,
                seat_number=seat_number,
                role=role,
            )
            return await self._db.get_game_by_id(game_id=game_id)

import random
from typing import ClassVar


class GetSeatUseCase:
    BASE_SEATS: ClassVar = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]

    @classmethod
    async def get_seat(cls, available_seats: list[int] | None) -> tuple[int | None, list[int]]:
        if available_seats is None:
            available_seats = cls.BASE_SEATS.copy()
        if not available_seats:
            return None, available_seats
        seat = random.choice(available_seats)
        available_seats.remove(seat)
        return seat, available_seats

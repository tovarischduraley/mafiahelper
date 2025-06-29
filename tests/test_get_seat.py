from contextlib import AbstractContextManager
from contextlib import nullcontext as does_not_raise
from itertools import permutations

import pytest

from usecases.get_seat import GetSeatUseCase


@pytest.mark.parametrize(
    ("allowed_seats", "allowed_values", "expectation"),
    (
        ([1], ([1], [()]), does_not_raise()),
        ([], ([None], [()]), does_not_raise()),
        (
            None,
            ([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], list(permutations([1, 2, 3, 4, 5, 6, 7, 8, 9, 10], 9))),
            does_not_raise(),
        ),
        ([1, 2, 3], ([1, 2, 3], list(permutations([1, 2, 3], 2))), does_not_raise()),
    ),
)
@pytest.mark.asyncio
async def test_get_seat(
    allowed_seats: list[int] | None,
    allowed_values: tuple[list, list[list[int]]],
    expectation: AbstractContextManager,
):
    uc = GetSeatUseCase()
    with expectation:
        seat, result_seats = await uc.get_seat(allowed_seats)
        assert seat in allowed_values[0]
        assert tuple(result_seats) in allowed_values[1]

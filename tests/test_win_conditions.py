from contextlib import nullcontext as does_not_raise
from typing import ContextManager

import pytest

from src.core import GameResults, Roles, get_win_result_by_user_role


@pytest.mark.parametrize(
    ("role", "result", "expectation"),
    (
        (Roles.CIVILIAN, GameResults.CIVILIANS_WON, does_not_raise()),
        (Roles.SHERIFF, GameResults.CIVILIANS_WON, does_not_raise()),
        (Roles.MAFIA, GameResults.MAFIA_WON, does_not_raise()),
        (Roles.DON, GameResults.MAFIA_WON, does_not_raise()),
        ("SomeRole", ..., pytest.raises(Exception)),
    ),
)
def test_win_results(role: Roles, result: GameResults, expectation: ContextManager) -> None:
    with expectation:
        assert get_win_result_by_user_role(role) == result
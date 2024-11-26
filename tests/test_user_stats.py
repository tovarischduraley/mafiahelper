from contextlib import nullcontext as does_not_raise

import pytest

from core import Roles
from tests.conftest import id_g, lost_game, won_game
from tests.mocks import FakeDBRepository
from usecases import GetUserStatsUseCase
from usecases.schemas import GameSchema, PlayerSchema, UserSchema, UserStatsSchema

test_user_id = next(id_g)
test_user = UserSchema(
    id=test_user_id,
    fio="Test Stats User",
    nickname="Test Stats User",
)
civilian = PlayerSchema(
    id=test_user_id,
    fio=test_user.fio,
    nickname=test_user.nickname,
    role=Roles.CIVILIAN,
    number=1
)
mafia = PlayerSchema(
    id=test_user_id,
    fio=test_user.fio,
    nickname=test_user.nickname,
    role=Roles.MAFIA,
    number=1
)
don = PlayerSchema(
    id=test_user_id,
    fio=test_user.fio,
    nickname=test_user.nickname,
    role=Roles.DON,
    number=1
)
sheriff = PlayerSchema(
    id=test_user.id,
    fio=test_user.fio,
    nickname=test_user.nickname,
    role=Roles.SHERIFF,
    number=1
)


@pytest.mark.parametrize(
    ("user", "games", "stats", "expectation"),
    (
            (test_user,
             [won_game(civilian), won_game(civilian)],
             UserStatsSchema(fio=test_user.fio, nickname=test_user.nickname, games_count_total=2,
                             win_percent_general=100, win_percent_black_team=None, win_percent_red_team=100,
                             win_percent_as_civilian=100, win_percent_as_mafia=None, win_percent_as_don=None,
                             win_percent_as_sheriff=None),
             does_not_raise()),
            (test_user,
             [won_game(mafia), won_game(civilian), lost_game(civilian), won_game(sheriff)],
             UserStatsSchema(fio=test_user.fio, nickname=test_user.nickname, games_count_total=4,
                             win_percent_general=75, win_percent_black_team=100,
                             win_percent_red_team=round(100 * 2 / 3, 2),
                             win_percent_as_civilian=50, win_percent_as_mafia=100, win_percent_as_don=None,
                             win_percent_as_sheriff=100),
             does_not_raise()),
            (test_user,
             [],
             UserStatsSchema(fio=test_user.fio, nickname=test_user.nickname, games_count_total=0,
                             win_percent_general=None, win_percent_black_team=None, win_percent_red_team=None,
                             win_percent_as_civilian=None, win_percent_as_mafia=None, win_percent_as_don=None,
                             win_percent_as_sheriff=None),
             does_not_raise()),
    ),
)
@pytest.mark.asyncio
async def test_user_stats(
        user: UserSchema,
        games: list[GameSchema],
        stats: UserStatsSchema,
        expectation: UserStatsSchema
):
    db = FakeDBRepository(games={game.id: game for game in games}, users={user.id: user})
    uc = GetUserStatsUseCase(db)
    with expectation:
        result = await uc.get_user_stats(user_id=user.id)
        assert result == stats

from contextlib import AbstractContextManager
from contextlib import nullcontext as does_not_raise

import pytest

from core import Roles
from tests.conftest import id_g, lost_game, won_game
from tests.mocks import FakeDBRepository
from usecases import GetPlayerStatsUseCase
from usecases.schemas import GameSchema, PlayerInGameSchema, PlayerSchema, PlayerStatsSchema

test_player_id = next(id_g)
test_player = PlayerSchema(
    id=test_player_id,
    fio="Test Stats User",
    nickname="Test Stats User",
)
civilian = PlayerInGameSchema(
    id=test_player_id, fio=test_player.fio, nickname=test_player.nickname, role=Roles.CIVILIAN, number=1
)
mafia = PlayerInGameSchema(
    id=test_player_id, fio=test_player.fio, nickname=test_player.nickname, role=Roles.MAFIA, number=1
)
don = PlayerInGameSchema(
    id=test_player_id, fio=test_player.fio, nickname=test_player.nickname, role=Roles.DON, number=1
)
sheriff = PlayerInGameSchema(
    id=test_player.id, fio=test_player.fio, nickname=test_player.nickname, role=Roles.SHERIFF, number=1
)


@pytest.mark.parametrize(
    ("player", "games", "stats", "expectation"),
    (
        (
            test_player,
            [won_game(civilian), won_game(civilian)],
            PlayerStatsSchema(
                fio=test_player.fio,
                nickname=test_player.nickname,
                games_count_total=2,
                win_percent_general=100,
                win_percent_black_team=None,
                win_percent_red_team=100,
                win_percent_as_civilian=100,
                win_percent_as_mafia=None,
                win_percent_as_don=None,
                win_percent_as_sheriff=None,
            ),
            does_not_raise(),
        ),
        (
            test_player,
            [won_game(mafia), won_game(civilian), lost_game(civilian), won_game(sheriff)],
            PlayerStatsSchema(
                fio=test_player.fio,
                nickname=test_player.nickname,
                games_count_total=4,
                win_percent_general=75,
                win_percent_black_team=100,
                win_percent_red_team=round(100 * 2 / 3, 2),
                win_percent_as_civilian=50,
                win_percent_as_mafia=100,
                win_percent_as_don=None,
                win_percent_as_sheriff=100,
            ),
            does_not_raise(),
        ),
        (
            test_player,
            [],
            PlayerStatsSchema(
                fio=test_player.fio,
                nickname=test_player.nickname,
                games_count_total=0,
                win_percent_general=None,
                win_percent_black_team=None,
                win_percent_red_team=None,
                win_percent_as_civilian=None,
                win_percent_as_mafia=None,
                win_percent_as_don=None,
                win_percent_as_sheriff=None,
            ),
            does_not_raise(),
        ),
    ),
)
@pytest.mark.asyncio
async def test_player_stats(
    player: PlayerSchema, games: list[GameSchema], stats: PlayerStatsSchema, expectation: AbstractContextManager
):
    db = FakeDBRepository(games={game.id: game for game in games}, players={player.id: player})
    uc = GetPlayerStatsUseCase(db)
    with expectation:
        result = await uc.get_player_stats(player_id=player.id)
        assert result == stats

from contextlib import AbstractContextManager
from contextlib import nullcontext as does_not_raise

import pytest
from conftest import id_g, lost_game, won_game
from mocks import FakeDBRepository

from core import Roles
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
                games_count_as_civilian=2,
                games_count_red_team=2,
                games_count_black_team=0,
                games_count_as_don=0,
                games_count_as_mafia=0,
                games_count_as_sheriff=0,
                won_games_count_as_civilian=2,
                won_games_count_as_don=0,
                won_games_count_as_mafia=0,
                won_games_count_as_sheriff=0,
                won_games_count_black_team=0,
                won_games_count_red_team=2,
                won_games_count_total=2,
                first_killed_count=0,
                best_move_count_total=0,
                zero_mafia_best_move_count=0,
                one_mafia_best_move_count=0,
                two_mafia_best_move_count=0,
                three_mafia_best_move_count=0,
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
                games_count_as_civilian=2,
                games_count_red_team=3,
                games_count_black_team=1,
                games_count_as_don=0,
                games_count_as_mafia=1,
                games_count_as_sheriff=1,
                won_games_count_as_civilian=1,
                won_games_count_as_don=0,
                won_games_count_as_mafia=1,
                won_games_count_as_sheriff=1,
                won_games_count_black_team=1,
                won_games_count_red_team=2,
                won_games_count_total=3,
                first_killed_count=0,
                best_move_count_total=0,
                zero_mafia_best_move_count=0,
                one_mafia_best_move_count=0,
                two_mafia_best_move_count=0,
                three_mafia_best_move_count=0,
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
                games_count_as_civilian=0,
                games_count_red_team=0,
                games_count_black_team=0,
                games_count_as_don=0,
                games_count_as_mafia=0,
                games_count_as_sheriff=0,
                won_games_count_as_civilian=0,
                won_games_count_as_don=0,
                won_games_count_as_mafia=0,
                won_games_count_as_sheriff=0,
                won_games_count_black_team=0,
                won_games_count_red_team=0,
                won_games_count_total=0,
                first_killed_count=0,
                best_move_count_total=0,
                zero_mafia_best_move_count=0,
                one_mafia_best_move_count=0,
                two_mafia_best_move_count=0,
                three_mafia_best_move_count=0,
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
        assert result.games_count_total == stats.games_count_total
        assert result.win_percent_general == stats.win_percent_general
        assert result.win_percent_black_team == stats.win_percent_black_team
        assert result.win_percent_red_team == stats.win_percent_red_team
        assert result.win_percent_as_civilian == stats.win_percent_as_civilian
        assert result.win_percent_as_mafia == stats.win_percent_as_mafia
        assert result.win_percent_as_don == stats.win_percent_as_don
        assert result.win_percent_as_sheriff == stats.win_percent_as_sheriff
        assert result.games_count_as_civilian == stats.games_count_as_civilian
        assert result.games_count_red_team == stats.games_count_red_team
        assert result.games_count_black_team == stats.games_count_black_team
        assert result.games_count_as_don == stats.games_count_as_don
        assert result.games_count_as_mafia == stats.games_count_as_mafia
        assert result.games_count_as_sheriff == stats.games_count_as_sheriff
        assert result.won_games_count_as_civilian == stats.won_games_count_as_civilian
        assert result.won_games_count_as_don == stats.won_games_count_as_don
        assert result.won_games_count_as_mafia == stats.won_games_count_as_mafia
        assert result.won_games_count_as_sheriff == stats.won_games_count_as_sheriff
        assert result.won_games_count_black_team == stats.won_games_count_black_team
        assert result.won_games_count_red_team == stats.won_games_count_red_team
        assert result.won_games_count_total == stats.won_games_count_total
        assert result.first_killed_count == stats.first_killed_count
        assert result.best_move_count_total == stats.best_move_count_total
        assert result.zero_mafia_best_move_count == stats.zero_mafia_best_move_count
        assert result.one_mafia_best_move_count == stats.one_mafia_best_move_count
        assert result.two_mafia_best_move_count == stats.two_mafia_best_move_count
        assert result.three_mafia_best_move_count == stats.three_mafia_best_move_count

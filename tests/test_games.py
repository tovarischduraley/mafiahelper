import datetime
from contextlib import AbstractContextManager
from contextlib import nullcontext as does_not_raise

import pytest

from core import GameResults, GameStatuses, Roles
from tests.conftest import (
    game_with_invalid_players_quantity,
    game_with_invalid_roles_distribution,
    game_with_nine_players,
    valid_game,
    valid_player,
)
from tests.mocks import FakeDBRepository
from usecases import AssignPlayerToSeatUseCase, CreateGameUseCase, EndGameUseCase
from usecases.errors import ValidationError
from usecases.schemas import GameSchema, PlayerSchema


@pytest.mark.asyncio
async def test_create_game_in_draft():
    db = FakeDBRepository()
    uc = CreateGameUseCase(db=db)
    now = datetime.datetime.now()
    users_count_before = len(db._games)
    created_game = await uc.create_game_in_draft(created_at=now)
    assert created_game == GameSchema(
        id=1,
        comments="",
        result=None,
        status=GameStatuses.DRAFT,
        players=[],
        created_at=now,
    )
    assert users_count_before + 1 == len(db._games)


@pytest.mark.parametrize(
    ("game", "game_result", "expectation"),
    (
        (valid_game(), GameResults.MAFIA_WON, does_not_raise()),
        (valid_game(), None, pytest.raises(ValidationError)),
        (game_with_invalid_roles_distribution(), GameResults.DRAW, pytest.raises(ValidationError)),
        (game_with_invalid_players_quantity(), GameResults.CIVILIANS_WON, pytest.raises(ValidationError)),
        (game_with_nine_players(), GameResults.MAFIA_WON, does_not_raise()),
    ),
)
@pytest.mark.asyncio
async def test_end_game(
    game: GameSchema,
    game_result: GameResults,
    expectation: AbstractContextManager,
):
    with expectation:
        db = FakeDBRepository(games={game.id: game})
        uc = EndGameUseCase(db=db)
        await uc.end_game(game_id=game.id, result=game_result)
        assert db._games[game.id].result == game_result
        assert db._games[game.id].status == GameStatuses.ENDED


@pytest.mark.parametrize(
    ("game", "player", "seat_number", "role", "expectation"),
    (
        (valid_game(), valid_player(), 1, Roles.MAFIA, does_not_raise()),
        (valid_game(), valid_player(), "10", Roles.CIVILIAN, pytest.raises(ValidationError)),
        (valid_game(), valid_player(), 11, Roles.CIVILIAN, pytest.raises(ValidationError)),
        (valid_game(), valid_player(), 2.5, Roles.CIVILIAN, pytest.raises(ValidationError)),
    ),
)
@pytest.mark.asyncio
async def test_assign_player_to_seat(
    game: GameSchema,
    player: PlayerSchema,
    seat_number: int,
    role: Roles,
    expectation: AbstractContextManager,
):
    with expectation:
        db = FakeDBRepository(players={player.id: player}, games={game.id: game})
        uc = AssignPlayerToSeatUseCase(db=db)
        result_game = await uc.assign_player_to_seat(
            game_id=game.id,
            player_id=player.id,
            seat_number=seat_number,
            role=role,
        )
        player_on_seat = next(filter(lambda p: p.number == seat_number, result_game.players))
        assert player.id == player_on_seat.id
        assert role == player_on_seat.role

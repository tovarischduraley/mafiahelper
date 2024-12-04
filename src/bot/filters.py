import time

from aiogram.filters.callback_data import CallbackData

import core


class GameSeatPlayerRoleCallbackFactory(CallbackData, prefix="game_seat_player_role"):
    game_id: int
    seat_number: int
    player_id: int
    role: core.Roles


class GameSeatPlayerCallbackFactory(CallbackData, prefix="game_seat_player"):
    game_id: int
    seat_number: int
    player_id: int


class GameSeatCallbackFactory(CallbackData, prefix="game_seat"):
    game_id: int
    seat_number: int
    page: int


class GameCallbackFactory(CallbackData, prefix="game"):
    game_id: int


class SelectResultCallbackFactory(CallbackData, prefix="result"):
    game_id: int


class EndGameCallbackFactory(CallbackData, prefix="end"):
    game_id: int
    result: core.GameResults


class PlayerCallbackFactory(CallbackData, prefix="player"):
    player_id: int
    players_page: int


class PlayersCurrentPageCallbackFactory(CallbackData, prefix="players"):
    page: int


class GetSeatCallbackFactory(CallbackData, prefix="seats"):
    allowed_seats: str | None
    timestamp: str = str(time.time() * 1000)

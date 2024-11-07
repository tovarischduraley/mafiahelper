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


class GameCallbackFactory(CallbackData, prefix="game"):
    game_id: int

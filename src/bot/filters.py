from aiogram.filters.callback_data import CallbackData


class GameSeatCallbackFactory(CallbackData, prefix='game_seat'):
    game_id: int
    seat_number: int

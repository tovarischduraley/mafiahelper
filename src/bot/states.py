from aiogram.fsm.state import State, StatesGroup


class CreatePlayerStates(StatesGroup):
    waiting_nickname = State()
    waiting_fio = State()

class UpdatePlayerStates(StatesGroup):
    setting_nickname = State()
    setting_avatar = State()

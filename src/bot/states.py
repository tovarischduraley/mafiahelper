from aiogram.fsm.state import State, StatesGroup


class CreatePlayerStates(StatesGroup):
    waiting_nickname = State()
    waiting_fio = State()

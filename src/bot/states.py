from aiogram.fsm.state import State, StatesGroup


class CreateUserStates(StatesGroup):
    waiting_nickname = State()
    waiting_fio = State()

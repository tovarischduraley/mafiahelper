from aiogram import F, Router, types
from aiogram.fsm.context import FSMContext

from bot import keyboards
from bot.states import CreateUserStates
from dependencies import container
from usecases import CreateUserUseCase, GetUsersUseCase
from usecases.schemas import CreateUserSchema

router = Router()


@router.message(F.text.lower() == "список игроков")
async def players(message: types.Message):
    uc: GetUsersUseCase = container.resolve(GetUsersUseCase)
    users = await uc.get_users()
    text = "Зарегистрированные пользователи:\nID nickname fio\n"
    await message.answer(
        text=text + "\n".join([f"{u.id} {u.nickname} {u.fio}" for u in users]),
    )


@router.message(F.text.lower() == "создать игрока")
async def create_player(message: types.Message, state: FSMContext):
    await message.answer("Введите ФИО игрока")
    await state.set_state(CreateUserStates.waiting_fio)


@router.message(CreateUserStates.waiting_fio, F.text)
async def process_user_fio(message: types.Message, state: FSMContext):
    await state.update_data(fio=message.text)
    await message.answer("Введите игровой псевдоним игрока")
    await state.set_state(CreateUserStates.waiting_nickname)


@router.message(CreateUserStates.waiting_nickname, F.text)
async def process_user_nickname(message: types.Message, state: FSMContext):
    await state.update_data(nickname=message.text)
    uc: CreateUserUseCase = container.resolve(CreateUserUseCase)
    user_data = await state.get_data()
    await uc.create_user(CreateUserSchema(**user_data))
    await message.answer(
        text=f"Вы создали игрока!\n\nИмя: {user_data["fio"]}\nПсевдоним: {user_data["nickname"]}",
        reply_markup=keyboards.menu,
    )
    await state.clear()

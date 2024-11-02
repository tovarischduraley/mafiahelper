import asyncio
import logging

from aiogram.utils.formatting import Bold

import keyboards
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters.command import Command
from aiogram.fsm.context import FSMContext

from bot.states import CreateUserStates
from config import settings
from dependencies import container
from usecases import CreateUserUseCase, GetUsersUseCase
from usecases.schemas import CreateUserSchema

logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    await message.answer(
        text="Выберите опцию",
        reply_markup=keyboards.menu,
    )


@dp.message(F.text.lower() == "список игроков")
async def players(message: types.Message):
    uc: GetUsersUseCase = container.resolve(GetUsersUseCase)
    users = await uc.get_users()
    text = "Зарегистрированные пользователи:\nID nickname fio\n"
    await message.answer(
        text=text + "\n".join([f"{u.id} {u.nickname} {u.fio}" for u in users]),
    )


@dp.message(F.text.lower() == "создать игрока")
async def create_player(message: types.Message, state: FSMContext):
    await message.answer("Введите ФИО игрока")
    await state.set_state(CreateUserStates.waiting_fio)


@dp.message(CreateUserStates.waiting_fio, F.text)
async def process_user_fio(message: types.Message, state: FSMContext):
    await state.update_data(fio=message.text)
    await message.answer("Введите игровой псевдоним игрока")
    await state.set_state(CreateUserStates.waiting_nickname)


@dp.message(CreateUserStates.waiting_nickname, F.text)
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


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

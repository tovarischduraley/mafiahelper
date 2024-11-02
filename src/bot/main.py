import asyncio
import logging

import keyboards
from aiogram import Bot, Dispatcher, F, types
from aiogram.filters.command import Command

from config import settings

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
    await message.answer("СПИСОК!")


@dp.message(F.text.lower() == "создать игрока")
async def create_player(message: types.Message):
    await message.answer("Введите ФИО игрока")


@dp.message(F.text.lower() == "создать игру")
async def create_game(message: types.Message):
    await message.answer("Форма создания игры!")


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

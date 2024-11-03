import asyncio
import logging

import keyboards
from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

from bot.routes import games_router, users_router
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


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    dp.include_routers(games_router, users_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

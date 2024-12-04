import asyncio
import logging

from aiogram import Bot, Dispatcher, types
from aiogram.filters.command import Command

from bot.auth import validate_admin
from bot.keyboards import admin_kb, user_kb
from bot.middleware import SaveUserMiddleware
from bot.routes import games_router, players_router
from config import settings
from usecases.errors import ForbiddenError

logging.basicConfig(level=logging.INFO)

bot = Bot(token=settings.TELEGRAM_BOT_TOKEN)
dp = Dispatcher()


@dp.message(Command("start"))
async def cmd_start(message: types.Message):
    try:
        validate_admin(message.from_user.id)
        await message.answer(
            text="Выберите опцию",
            reply_markup=admin_kb,
        )
    except ForbiddenError:
        await message.answer(
            text="Выберите опцию",
            reply_markup=user_kb,
        )


async def main():
    await bot.delete_webhook(drop_pending_updates=True)
    dp.message.middleware(SaveUserMiddleware())
    dp.callback_query.middleware(SaveUserMiddleware())
    dp.include_routers(games_router, players_router)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())

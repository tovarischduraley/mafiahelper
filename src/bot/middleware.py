from typing import Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

from config import settings
from dependencies import container
from usecases import UsersUseCase
from usecases.schemas import UserSchema


class SaveUserMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable, event: TelegramObject, data: dict):
        user: User = data["event_from_user"]
        users_uc: UsersUseCase = container.resolve(UsersUseCase)
        if user.id not in {u.telegram_id for u in await users_uc.get_users()}:
            user_to_save = UserSchema(
                telegram_id=user.id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
            )
            await users_uc.save_user(user_to_save)
            if user.id != settings.ADMIN_ID:
                await event.bot.send_message(settings.ADMIN_ID, text=self._get_new_user_message(user_to_save))
        return await handler(event, data)

    @staticmethod
    def _get_new_user_message(user: UserSchema) -> str:
        return (f"Новый пользователь бота:\n"
                f"ID: {user.telegram_id}\n"
                f"Имя: {user.first_name} {user.last_name or ""}"
                f"\n\n{"" + user.username or ""}")

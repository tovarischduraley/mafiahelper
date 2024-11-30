from typing import Callable

from aiogram import BaseMiddleware
from aiogram.types import TelegramObject, User

from dependencies import container
from usecases import GetUsersUseCase


class SomeMiddleware(BaseMiddleware):
    async def __call__(self, handler: Callable, event: TelegramObject, data: dict):
        user: User = data["event_from_user"]
        get_uc: GetUsersUseCase = container.resolve(GetUsersUseCase)
        save_uc: SaveUserUseCase = container.resolve(Sa)
        if user.id not in {u.id for u in await uc.get_players()}:


        result = await handler(event, data)
        print("After handler")

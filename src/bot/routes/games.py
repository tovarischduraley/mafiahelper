import datetime

from aiogram import F, Router, types
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.filters import GameSeatCallbackFactory
from dependencies import container
from usecases.create_game import CreateGameUseCase
from usecases.schemas.games import PlayerSchema

router = Router()


def _get_nickname_by_number(number: int, players: list[PlayerSchema]) -> str:
    if player := next(filter(lambda p: p.number == number, players), None):
        return player.nickname
    return "--"


@router.message(F.text.lower() == "создать игру")
async def create_game(message: types.Message):
    uc: CreateGameUseCase = container.resolve(CreateGameUseCase)
    now = datetime.datetime.now()
    game = await uc.create_game_in_draft(now)
    builder = InlineKeyboardBuilder()
    for number in range(1, 11):
        builder.button(
            text=f"{number}. {_get_nickname_by_number(number, game.players)}",
            callback_data=GameSeatCallbackFactory(game_id=game.id, seat_number=number),
        )
    builder.adjust(5)
    await message.answer(text=f"Игра {now.strftime("%d.%m.%Y %H:%m")}", reply_markup=builder.as_markup())


@router.callback_query(GameSeatCallbackFactory.filter())
async def set_player_game_number(callback_query: types.CallbackQuery, callback_data: GameSeatCallbackFactory): ...

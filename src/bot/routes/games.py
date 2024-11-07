import datetime

from aiogram import F, Router, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import core
from bot.filters import (
    GameCallbackFactory,
    GameSeatCallbackFactory,
    GameSeatPlayerCallbackFactory,
    GameSeatPlayerRoleCallbackFactory,
)
from dependencies import container
from usecases import GetUsersUseCase
from usecases.create_game import CreateGameUseCase
from usecases.get_game import GetGameUseCase
from usecases.schemas import GameSchema
from usecases.schemas.games import PlayerSchema

router = Router()


def _get_nickname_by_number(number: int, players: list[PlayerSchema]) -> str:
    if player := next(filter(lambda p: p.number == number, players), None):
        return player.nickname
    return "--"


def _get_game_keyboard(game: GameSchema) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for number in range(1, 11):
        builder.button(
            text=f"{number}. {_get_nickname_by_number(number, game.players)}",
            callback_data=GameSeatCallbackFactory(game_id=game.id, seat_number=number),
        )
    builder.button(text="Завершить игру", callback_data=GameCallbackFactory(game_id=game.id))
    builder.adjust(5)
    return builder.as_markup()


@router.message(F.text.lower() == "создать игру")
async def create_game(message: types.Message):
    uc: CreateGameUseCase = container.resolve(CreateGameUseCase)
    now = datetime.datetime.now()
    game = await uc.create_game_in_draft(created_at=now)
    await message.answer(text=f"Игра {now.strftime("%d.%m.%Y %H:%m")}", reply_markup=_get_game_keyboard(game))

@router.callback_query(GameSeatPlayerCallbackFactory.filter())
async def assign_player_to_seat(query: types.CallbackQuery, callback_data: GameSeatPlayerRoleCallbackFactory):
    ...

@router.callback_query(GameSeatPlayerCallbackFactory.filter())
async def select_role(callback_query: types.CallbackQuery, callback_data: GameSeatPlayerCallbackFactory):
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Мафия",
                    callback_data=GameSeatPlayerRoleCallbackFactory(
                        role=core.Roles.MAFIA, **callback_data.model_dump()
                    ),
                ),
                InlineKeyboardButton(
                    text="Шериф",
                    callback_data=GameSeatPlayerRoleCallbackFactory(
                        role=core.Roles.SHERIFF, **callback_data.model_dump()
                    ),
                ),
                InlineKeyboardButton(
                    text="Мирный житель",
                    callback_data=GameSeatPlayerRoleCallbackFactory(
                        role=core.Roles.CIVILIAN, **callback_data.model_dump()
                    ),
                ),
                InlineKeyboardButton(
                    text="Дон",
                    callback_data=GameSeatPlayerRoleCallbackFactory(role=core.Roles.DON, **callback_data.model_dump()),
                ),
            ],
        ]
    )
    await callback_query.message.edit_text(
        text="Выберите роль:",
        reply_markup=kb,
    )
    await callback_query.answer()


@router.callback_query(GameSeatCallbackFactory.filter())
async def select_player(callback_query: types.CallbackQuery, callback_data: GameSeatCallbackFactory):
    builder = InlineKeyboardBuilder()
    uc: GetUsersUseCase = container.resolve(GetUsersUseCase)
    users = await uc.get_users(limit=10)
    for user in users:
        builder.button(
            text=f"{user.nickname}",
            callback_data=GameSeatPlayerCallbackFactory(
                game_id=callback_data.game_id,
                seat_number=callback_data.seat_number,
                player_id=user.id,
            ),
        )
    builder.row(
        InlineKeyboardButton(text="⬅️", callback_data="test"),
        InlineKeyboardButton(text="Отмена", callback_data=f"game:{callback_data.game_id}"),
        InlineKeyboardButton(text="➡️", callback_data="test"),
    )

    await callback_query.message.edit_text(
        text=f"Выберите игрока на стул №{callback_data.seat_number}",
        reply_markup=builder.as_markup(),
    )
    await callback_query.answer()


@router.callback_query(GameCallbackFactory.filter())
async def get_game_info(callback_query: types.CallbackQuery, callback_data: GameCallbackFactory):
    uc: GetGameUseCase = container.resolve(GetGameUseCase)
    game = await uc.get_game(callback_data.game_id)
    await callback_query.message.edit_text(
        text=f"Игра {game.created_at.strftime('%d.%m.%Y %H:%m')}", reply_markup=_get_game_keyboard(game)
    )
    await callback_query.answer()

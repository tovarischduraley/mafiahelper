import datetime

from aiogram import F, Router, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import core
from bot.auth import validate_admin
from bot.filters import (
    EndGameCallbackFactory,
    GameCallbackFactory,
    GameSeatCallbackFactory,
    GameSeatPlayerCallbackFactory,
    GameSeatPlayerRoleCallbackFactory,
    GetSeatCallbackFactory,
    SelectResultCallbackFactory,
)
from bot.utils import get_role_emoji
from dependencies import container
from usecases import AssignPlayerToSeatUseCase, CreateGameUseCase, EndGameUseCase, GetGameUseCase, GetPlayersUseCase
from usecases.errors import ValidationError
from usecases.get_seat import GetSeatUseCase
from usecases.schemas import GameSchema, PlayerInGameSchema, PlayerSchema

router = Router()
PLAYERS_PER_PAGE = 10


def _get_player_by_number(number: int, players: list[PlayerInGameSchema]) -> PlayerInGameSchema | None:
    if player := next(filter(lambda p: p.number == number, players), None):
        return player
    return None


def _get_players_builder(players: list[PlayerSchema], seat_number: int, game_id: int) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for player in players:
        builder.button(
            text=f"{player.nickname}",
            callback_data=GameSeatPlayerCallbackFactory(
                game_id=game_id,
                seat_number=seat_number,
                player_id=player.id,
            ),
        )
    builder.adjust(2)
    return builder


def _get_game_keyboard(game: GameSchema) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for number in [5,6,4,7,3,8,2,9,1,10]:
        player = _get_player_by_number(number, game.players)
        builder.button(
            text=f"{number}. {player.nickname + " " + get_role_emoji(player.role) if player else "--"}",
            callback_data=GameSeatCallbackFactory(game_id=game.id, seat_number=number, page=0),
        )
    builder.button(text="Завершить игру", callback_data=SelectResultCallbackFactory(game_id=game.id))
    builder.adjust(2)
    return builder.as_markup()


def _get_end_game_text(game: GameSchema) -> str:
    sorted_players = sorted(game.players, key=lambda p: p.number)
    players_text = "\n".join([f"{p.number} {p.nickname} {get_role_emoji(p.role)}" for p in sorted_players])
    return (
        f"Игра {game.created_at.strftime("%d.%m.%Y %H:%m")} завершена\n"
        f"Результат: {core.get_result_text(game.result)}\n\n"
        f"{players_text}"
    )


@router.callback_query(EndGameCallbackFactory.filter())
async def end_game(callback_query: types.CallbackQuery, callback_data: EndGameCallbackFactory):
    validate_admin(callback_query.from_user.id)
    end_uc: EndGameUseCase = container.resolve(EndGameUseCase)
    get_uc: GetGameUseCase = container.resolve(GetGameUseCase)
    try:
        await end_uc.end_game(game_id=callback_data.game_id, result=callback_data.result)
        game = await get_uc.get_game(callback_data.game_id)
        await callback_query.message.edit_text(text=_get_end_game_text(game))
    except ValidationError as e:
        await callback_query.answer(text=str(e))


@router.callback_query(SelectResultCallbackFactory.filter())
async def select_game_result(callback_query: types.CallbackQuery, callback_data: SelectResultCallbackFactory):
    validate_admin(callback_query.from_user.id)
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Победа города",
        callback_data=EndGameCallbackFactory(game_id=callback_data.game_id, result=core.GameResults.CIVILIANS_WON),
    )
    builder.button(
        text="Победа мафии",
        callback_data=EndGameCallbackFactory(game_id=callback_data.game_id, result=core.GameResults.MAFIA_WON),
    )
    builder.button(
        text="Ничья",
        callback_data=EndGameCallbackFactory(game_id=callback_data.game_id, result=core.GameResults.DRAW),
    )
    builder.button(
        text="Отмена",
        callback_data=GameCallbackFactory(game_id=callback_data.game_id),
    )
    builder.adjust(1)
    await callback_query.message.edit_text("Выберите исход игры", reply_markup=builder.as_markup())
    await callback_query.answer()


@router.message(F.text.lower() == "создать игру")
async def create_game(message: types.Message):
    validate_admin(message.from_user.id)
    uc: CreateGameUseCase = container.resolve(CreateGameUseCase)
    now = datetime.datetime.now()
    game = await uc.create_game_in_draft(created_at=now)
    await message.answer(text=f"Игра {now.strftime("%d.%m.%Y %H:%m")}", reply_markup=_get_game_keyboard(game))


@router.callback_query(GameSeatPlayerRoleCallbackFactory.filter())
async def assign_player_to_seat(callback_query: types.CallbackQuery, callback_data: GameSeatPlayerRoleCallbackFactory):
    validate_admin(callback_query.from_user.id)
    uc: AssignPlayerToSeatUseCase = container.resolve(AssignPlayerToSeatUseCase)
    game = await uc.assign_player_to_seat(
        game_id=callback_data.game_id,
        seat_number=callback_data.seat_number,
        player_id=callback_data.player_id,
        role=callback_data.role,
    )
    await callback_query.message.edit_text(
        text=f"Игра {game.created_at.strftime("%d.%m.%Y %H:%m")}",
        reply_markup=_get_game_keyboard(game),
    )
    await callback_query.answer()


@router.callback_query(GameSeatPlayerCallbackFactory.filter())
async def select_role(callback_query: types.CallbackQuery, callback_data: GameSeatPlayerCallbackFactory):
    validate_admin(callback_query.from_user.id)
    builder = InlineKeyboardBuilder()
    builder.button(
        text="Мафия",
        callback_data=GameSeatPlayerRoleCallbackFactory(role=core.Roles.MAFIA, **callback_data.model_dump()),
    )
    builder.button(
        text="Шериф",
        callback_data=GameSeatPlayerRoleCallbackFactory(role=core.Roles.SHERIFF, **callback_data.model_dump()),
    )
    builder.button(
        text="Мирный житель",
        callback_data=GameSeatPlayerRoleCallbackFactory(role=core.Roles.CIVILIAN, **callback_data.model_dump()),
    )
    builder.button(
        text="Дон",
        callback_data=GameSeatPlayerRoleCallbackFactory(role=core.Roles.DON, **callback_data.model_dump()),
    )
    builder.adjust(1)
    await callback_query.message.edit_text(
        text="Выберите роль:",
        reply_markup=builder.as_markup(),
    )
    await callback_query.answer()


@router.callback_query(GameSeatCallbackFactory.filter())
async def select_player(callback_query: types.CallbackQuery, callback_data: GameSeatCallbackFactory):
    validate_admin(callback_query.from_user.id)
    uc: GetPlayersUseCase = container.resolve(GetPlayersUseCase)
    players = await uc.get_players(limit=PLAYERS_PER_PAGE, offset=callback_data.page * PLAYERS_PER_PAGE)
    players_count = await uc.get_players_count()
    builder = _get_players_builder(players, seat_number=callback_data.seat_number, game_id=callback_data.game_id)
    builder.adjust(2)

    buttons = []
    if callback_data.page > 0:
        buttons.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=GameSeatCallbackFactory(
                    game_id=callback_data.game_id, seat_number=callback_data.seat_number, page=callback_data.page - 1
                ).pack(),
            ),
        )
    else:
        buttons.append(InlineKeyboardButton(text=" ", callback_data="lorem-ipsum"))
    buttons.append(
        InlineKeyboardButton(
            text="Отмена",
            callback_data=GameCallbackFactory(game_id=callback_data.game_id).pack(),
        )
    )
    if players_count > len(players) + callback_data.page * PLAYERS_PER_PAGE:
        buttons.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=GameSeatCallbackFactory(
                    game_id=callback_data.game_id, seat_number=callback_data.seat_number, page=callback_data.page + 1
                ).pack(),
            )
        )
    else:
        buttons.append(InlineKeyboardButton(text=" ", callback_data="lorem-ipsum"))
    if buttons:
        builder.row(*buttons, width=3)

    await callback_query.message.edit_text(
        text=f"Выберите игрока на стул №{callback_data.seat_number}",
        reply_markup=builder.as_markup(),
    )
    await callback_query.answer()


@router.callback_query(GameCallbackFactory.filter())
async def get_game_info(callback_query: types.CallbackQuery, callback_data: GameCallbackFactory):
    validate_admin(callback_query.from_user.id)
    uc: GetGameUseCase = container.resolve(GetGameUseCase)
    game = await uc.get_game(callback_data.game_id)
    await callback_query.message.edit_text(
        text=f"Игра {game.created_at.strftime('%d.%m.%Y %H:%m')}", reply_markup=_get_game_keyboard(game)
    )
    await callback_query.answer()


def _get_str_allowed_seats(allowed_seats: list[int]) -> str:
    return ", ".join(map(str, allowed_seats))


@router.message(F.text.lower() == "сгенерировать рассадку")
async def get_seats_distribution(message: types.Message):
    validate_admin(message.from_user.id)
    uc: GetSeatUseCase = container.resolve(GetSeatUseCase)
    seat, allowed_seats = await uc.get_seat(available_seats=None)
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(text="Заново", callback_data=GetSeatCallbackFactory(allowed_seats=None).pack()),
                InlineKeyboardButton(
                    text="Следующий",
                    callback_data=GetSeatCallbackFactory(allowed_seats=_get_str_allowed_seats(allowed_seats)).pack(),
                ),
            ],
        ]
    )
    await message.answer(
        text=f"Выданные места:\n{seat}\n\nОставшиеся места:\n{_get_str_allowed_seats(allowed_seats=allowed_seats)}",
        reply_markup=kb,
    )


def _get_distributed_seats_text(message_text: str, seat: int) -> str:
    numbers_row = message_text.split("\n")[1]
    return f"{numbers_row} -> {seat}"


def _parse_allowed_seats(str_allowed_seats: str | None) -> list[int]:
    return list(map(int, str_allowed_seats.split(", ")))


@router.callback_query(GetSeatCallbackFactory.filter())
async def get_new_seat(callback_query: types.CallbackQuery, callback_data: GetSeatCallbackFactory):
    validate_admin(callback_query.from_user.id)
    uc: GetSeatUseCase = container.resolve(GetSeatUseCase)
    parsed = _parse_allowed_seats(callback_data.allowed_seats) if callback_data.allowed_seats is not None else None
    seat, allowed_seats = await uc.get_seat(available_seats=parsed)
    builder = InlineKeyboardBuilder()
    to_start = InlineKeyboardButton(text="Заново", callback_data=GetSeatCallbackFactory(allowed_seats=None).pack())
    to_next = InlineKeyboardButton(
        text="Следующий",
        callback_data=GetSeatCallbackFactory(allowed_seats=_get_str_allowed_seats(allowed_seats)).pack(),
    )
    if callback_data.allowed_seats is None:
        text = f"Выданные места:\n{seat}\n\nОставшиеся места:\n{_get_str_allowed_seats(allowed_seats=allowed_seats)}"
        builder.row(to_start, to_next)
    elif not allowed_seats:
        text = f"Выданные места:\n{_get_distributed_seats_text(callback_query.message.text, seat=seat)}\n\n"
        builder.row(to_start)
    else:
        text = (
            f"Выданные места:\n"
            f"{_get_distributed_seats_text(callback_query.message.text, seat=seat)}\n\n"
            f"Оставшиеся места:\n{_get_str_allowed_seats(allowed_seats=allowed_seats)}"
        )
        builder.row(to_start, to_next)
    await callback_query.message.edit_text(text=text, reply_markup=builder.as_markup())
    await callback_query.answer()

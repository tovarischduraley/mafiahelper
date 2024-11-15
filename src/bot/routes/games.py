import datetime

from aiogram import F, Router, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot.filters import (
    EndGameCallbackFactory,
    GameCallbackFactory,
    GameSeatCallbackFactory,
    GameSeatPlayerCallbackFactory,
    GameSeatPlayerRoleCallbackFactory,
    SelectResultCallbackFactory,
)
from bot.utils import get_role_emoji
import core
from dependencies import container
from usecases import AssignPlayerToSeatUseCase, CreateGameUseCase, EndGameUseCase, GetGameUseCase, GetUsersUseCase
from usecases.errors import ValidationError
from usecases.schemas import GameSchema, PlayerSchema, UserSchema

router = Router()
USERS_PER_PAGE = 10

def _get_player_by_number(number: int, players: list[PlayerSchema]) -> PlayerSchema | None:
    if player := next(filter(lambda p: p.number == number, players), None):
        return player
    return None

def _get_users_builder(users: list[UserSchema], seat_number: int, game_id: int) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for user in users:
        builder.button(
            text=f"{user.nickname}",
            callback_data=GameSeatPlayerCallbackFactory(
                game_id=game_id,
                seat_number=seat_number,
                player_id=user.id,
            )
        )
    builder.adjust(2)
    return builder


def _get_game_keyboard(game: GameSchema) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for number in range(1, 11):
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
    uc: CreateGameUseCase = container.resolve(CreateGameUseCase)
    now = datetime.datetime.now()
    game = await uc.create_game_in_draft(created_at=now)
    await message.answer(text=f"Игра {now.strftime("%d.%m.%Y %H:%m")}", reply_markup=_get_game_keyboard(game))


@router.callback_query(GameSeatPlayerRoleCallbackFactory.filter())
async def assign_player_to_seat(callback_query: types.CallbackQuery, callback_data: GameSeatPlayerRoleCallbackFactory):
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
    builder = InlineKeyboardBuilder()
    (
        builder.button(
            text="Мафия",
            callback_data=GameSeatPlayerRoleCallbackFactory(role=core.Roles.MAFIA, **callback_data.model_dump()),
        ),
    )
    (
        builder.button(
            text="Шериф",
            callback_data=GameSeatPlayerRoleCallbackFactory(role=core.Roles.SHERIFF, **callback_data.model_dump()),
        ),
    )
    (
        builder.button(
            text="Мирный житель",
            callback_data=GameSeatPlayerRoleCallbackFactory(role=core.Roles.CIVILIAN, **callback_data.model_dump()),
        ),
    )
    (
        builder.button(
            text="Дон",
            callback_data=GameSeatPlayerRoleCallbackFactory(role=core.Roles.DON, **callback_data.model_dump()),
        ),
    )
    builder.adjust(1)
    await callback_query.message.edit_text(
        text="Выберите роль:",
        reply_markup=builder.as_markup(),
    )
    await callback_query.answer()


@router.callback_query(GameSeatCallbackFactory.filter())
async def select_player(callback_query: types.CallbackQuery, callback_data: GameSeatCallbackFactory):
    uc: GetUsersUseCase = container.resolve(GetUsersUseCase)
    users = await uc.get_users(limit=USERS_PER_PAGE, offset=callback_data.page * USERS_PER_PAGE)
    users_count = await uc.get_users_count()
    builder = _get_users_builder(users, seat_number=callback_data.seat_number, game_id=callback_data.game_id)
    builder.adjust(2)

    buttons = []
    if callback_data.page > 0:
        buttons.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=GameSeatCallbackFactory(
                    game_id=callback_data.game_id,
                    seat_number=callback_data.seat_number,
                    page=callback_data.page - 1
                ).pack()
            ),
        )
    else:
        buttons.append(
            InlineKeyboardButton(text=" ", callback_data="lorem-ipsum")
        )
    buttons.append(InlineKeyboardButton(
        text="Отмена",
        callback_data=GameCallbackFactory(game_id=callback_data.game_id).pack(),
    ))
    if users_count > len(users) + callback_data.page * USERS_PER_PAGE:
        buttons.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=GameSeatCallbackFactory(
                    game_id=callback_data.game_id,
                    seat_number=callback_data.seat_number,
                    page=callback_data.page + 1
                ).pack(),
            )
        )
    else:
        buttons.append(
            InlineKeyboardButton(text=" ", callback_data="lorem-ipsum")
        )
    if buttons:
        builder.row(*buttons,width=3)

    await callback_query.message.edit_text(
        text=f"Выберите игрока на стул №{callback_data.seat_number}",
        reply_markup=builder.as_markup(),
    )
    await callback_query.answer()
@router.callback_query(F.data.lower() == "lorem-ipsum")
async def lorem_ipsum(callback_query: types.CallbackQuery):
    await callback_query.answer()

@router.callback_query(GameCallbackFactory.filter())
async def get_game_info(callback_query: types.CallbackQuery, callback_data: GameCallbackFactory):
    uc: GetGameUseCase = container.resolve(GetGameUseCase)
    game = await uc.get_game(callback_data.game_id)
    await callback_query.message.edit_text(
        text=f"Игра {game.created_at.strftime('%d.%m.%Y %H:%m')}", reply_markup=_get_game_keyboard(game)
    )
    await callback_query.answer()

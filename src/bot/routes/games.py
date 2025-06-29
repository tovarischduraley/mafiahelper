import datetime

from aiogram import F, Router, types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

import core
from bot.auth import validate_admin
from bot.filters import (
    AddToBestMoveFactory,
    AssignAsFirstKilledFactory,
    EndGameCallbackFactory,
    GameCallbackFactory,
    GameSeatCallbackFactory,
    GameSeatPlayerCallbackFactory,
    GameSeatPlayerRoleCallbackFactory,
    GamesCurrentPageCallbackFactory,
    GamesDetailPageCallbackFactory,
    GetSeatCallbackFactory,
    RegisterFirstKilledFactory,
    SelectResultCallbackFactory,
)
from bot.utils import get_role_emoji, get_team_emoji_by_game_result
from core.games import GameStatuses, RolesQuantity
from dependencies import container
from usecases import (
    AddToBestMoveUseCase,
    AssignAsFirstKilledUseCase,
    AssignPlayerToSeatUseCase,
    CreateGameUseCase,
    EndGameUseCase,
    GetGamesUseCase,
    GetPlayersUseCase,
    GetSeatUseCase,
)
from usecases.errors import ValidationError
from usecases.schemas import GameSchema, PlayerInGameSchema, PlayerSchema

router = Router()
PLAYERS_PER_PAGE = 10
GAMES_PER_PAGE = 5
ORDERED_PLAYERS_NUMBERS = [5, 6, 4, 7, 3, 8, 2, 9, 1, 10]


def _get_player_by_number(number: int, players: set[PlayerInGameSchema]) -> PlayerInGameSchema | None:
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


def _get_games_builder(games: list[GameSchema], from_page: int) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for game in games:
        builder.button(
            text=f"{get_team_emoji_by_game_result(game.result)} {game.created_at.strftime("%d.%m.%Y %H:%M")}",
            callback_data=GamesDetailPageCallbackFactory(
                game_id=game.id,
                page=from_page,
            ).pack(),
        )
    builder.adjust(2)
    return builder


def _get_draft_game_keyboard(game: GameSchema) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for number in ORDERED_PLAYERS_NUMBERS:
        player = _get_player_by_number(number, game.players)
        builder.button(
            text=f"{number}. {player.nickname + " " + get_role_emoji(player.role) if player else "--"}",
            callback_data=GameSeatCallbackFactory(game_id=game.id, seat_number=number, page=0),
        )
    builder.adjust(2)
    if game.first_killed is None and len(game.players) == core.MAX_PLAYERS:
        builder.row(
            InlineKeyboardButton(
                text="Внести ПУ", callback_data=RegisterFirstKilledFactory(game_id=game.id).pack(), width=1
            )
        )
    builder.row(
        InlineKeyboardButton(
            text="Завершить игру", callback_data=SelectResultCallbackFactory(game_id=game.id).pack(), width=1
        )
    )
    return builder.as_markup()


def _get_draft_game_text(game: GameSchema) -> str:
    text = f"Игра {game.created_at.strftime("%d.%m.%Y %H:%M")}\n"
    if len(game.players) == core.MAX_PLAYERS:
        text += _get_best_move_text(first_killed=game.first_killed, best_move=game.best_move)
    return text


def _get_game_text_and_keyboard(game: GameSchema) -> tuple[str, InlineKeyboardMarkup | None]:
    match game.status:
        case GameStatuses.ENDED:
            text = _get_end_game_text(game=game)
            keyboard = None
        case GameStatuses.DRAFT:
            text = _get_draft_game_text(game=game)
            keyboard = _get_draft_game_keyboard(game=game)
        case _:
            raise Exception(f"Undefined game status '{game.status}'")
    return text, keyboard


def _get_best_move_text(
    first_killed: PlayerInGameSchema | None,
    best_move: set[PlayerInGameSchema] | None,
) -> str:
    if not best_move:
        best_move_text = "--"
    else:
        sorted_best_move = sorted(best_move, key=lambda p: p.number)
        best_move_text = (
            ", ".join([f"{p.number}" for p in sorted_best_move])
            + " ("
            + ", ".join([f"{p.nickname}" for p in sorted_best_move])
            + ")"
            if sorted_best_move
            else "--"
        )
    return f"ПУ: {first_killed.nickname if first_killed else "--"}\nЛХ: {best_move_text}\n"


def _get_end_game_text(game: GameSchema) -> str:
    sorted_players = sorted(game.players, key=lambda p: p.number)
    players_text = "\n".join([f"{p.number}. {p.nickname} {get_role_emoji(p.role)}" for p in sorted_players])
    return (
        f"Игра {game.created_at.strftime("%d.%m.%Y %H:%M")} завершена\n"
        f"Результат: {core.get_result_text(game.result)}\n"
        f"{_get_best_move_text(first_killed=game.first_killed, best_move=game.best_move)}\n"
        f"{players_text}"
    )


def _get_first_killed_keyboard(game: GameSchema) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for number in ORDERED_PLAYERS_NUMBERS:
        player = _get_player_by_number(number, game.players)
        builder.button(
            text=f"{number}. {player.nickname + " " + get_role_emoji(player.role) if player else "--"}",
            callback_data=AssignAsFirstKilledFactory(game_id=game.id, first_killed_number=number),
        )
    builder.adjust(2)
    builder.row(
        InlineKeyboardButton(
            text="Отмена",
            callback_data=GameCallbackFactory(game_id=game.id).pack(),
        )
    )
    return builder.as_markup()


def _get_best_move_keyboard(
    game: GameSchema,
    players_numbers_str: str = "",
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    for number in ORDERED_PLAYERS_NUMBERS:
        player = _get_player_by_number(number, game.players)
        added_numbers = set(players_numbers_str.split(","))
        if number in added_numbers:
            new_players_numbers_str = players_numbers_str
        else:
            new_players_numbers_str = f"{players_numbers_str},{number}" if players_numbers_str else str(number)
        builder.button(
            text=f"{number}. {player.nickname + " " + get_role_emoji(player.role) if player else "--"}",
            callback_data=AddToBestMoveFactory(
                game_id=game.id,
                players_numbers_str=new_players_numbers_str,
            ),
        )
    builder.button(
        text="Назад",
        callback_data=RegisterFirstKilledFactory(game_id=game.id),
    )
    builder.button(
        text="Без ЛХ",
        callback_data=GameCallbackFactory(game_id=game.id),
    )
    builder.adjust(2)
    return builder.as_markup()


@router.callback_query(RegisterFirstKilledFactory.filter())
async def register_first_killed(callback_query: types.CallbackQuery, callback_data: RegisterFirstKilledFactory):
    validate_admin(callback_query.from_user.id)
    uc: GetGamesUseCase = container.resolve(GetGamesUseCase)
    game = await uc.get_game(callback_data.game_id)
    await callback_query.message.edit_text(
        text="Выберите первого убиенного",
        reply_markup=_get_first_killed_keyboard(game=game),
    )
    await callback_query.answer()


@router.callback_query(AssignAsFirstKilledFactory.filter())
async def assign_as_first_killed(callback_query: types.CallbackQuery, callback_data: AssignAsFirstKilledFactory):
    validate_admin(callback_query.from_user.id)
    assign_uc: AssignAsFirstKilledUseCase = container.resolve(AssignAsFirstKilledUseCase)
    get_uc: GetGamesUseCase = container.resolve(GetGamesUseCase)
    game = await get_uc.get_game(callback_data.game_id)
    await assign_uc.assign_player_as_first_killed(
        game_id=callback_data.game_id,
        player_number=callback_data.first_killed_number,
    )
    await callback_query.message.edit_text(
        text="Добавьте игроков в лучший ход",
        reply_markup=_get_best_move_keyboard(game=game),
    )
    await callback_query.answer()


@router.callback_query(AddToBestMoveFactory.filter())
async def add_to_best_move(callback_query: types.CallbackQuery, callback_data: AddToBestMoveFactory):
    validate_admin(callback_query.from_user.id)
    players_numbers = set(callback_data.players_numbers_str.split(","))
    get_uc: GetGamesUseCase = container.resolve(GetGamesUseCase)
    game = await get_uc.get_game(callback_data.game_id)
    if len(players_numbers) != RolesQuantity.MAFIA + RolesQuantity.DON:
        await callback_query.message.edit_text(
            text=f"Добавьте игроков в лучший ход\nДобавлены: {", ".join(sorted(players_numbers))}\n",
            reply_markup=_get_best_move_keyboard(game=game, players_numbers_str=callback_data.players_numbers_str),
        )
    else:
        uc: AddToBestMoveUseCase = container.resolve(AddToBestMoveUseCase)
        await uc.add_players_to_best_move(
            game_id=callback_data.game_id,
            players_numbers=set(map(int, players_numbers)),
        )
        get_uc: GetGamesUseCase = container.resolve(GetGamesUseCase)
        game = await get_uc.get_game(callback_data.game_id)
        text, kb = _get_game_text_and_keyboard(game=game)
        await callback_query.message.edit_text(
            text=text,
            reply_markup=kb,
        )
    await callback_query.answer()


@router.callback_query(EndGameCallbackFactory.filter())
async def end_game(callback_query: types.CallbackQuery, callback_data: EndGameCallbackFactory):
    validate_admin(callback_query.from_user.id)
    end_uc: EndGameUseCase = container.resolve(EndGameUseCase)
    try:
        await end_uc.end_game(game_id=callback_data.game_id, result=callback_data.result)
        get_uc: GetGamesUseCase = container.resolve(GetGamesUseCase)
        game = await get_uc.get_game(callback_data.game_id)
        text, kb = _get_game_text_and_keyboard(game=game)
        await callback_query.message.edit_text(text=text, reply_markup=kb)
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


@router.message(F.text.lower() == "список игр")
async def games_list(message: types.Message):
    uc: GetGamesUseCase = container.resolve(GetGamesUseCase)
    games, games_count = await uc.get_ended_games(limit=GAMES_PER_PAGE)
    builder = _get_games_builder(games, from_page=0)
    builder.adjust(1)
    if not games:
        await message.answer(text="Список игр пуст.", reply_markup=builder.as_markup())
        return
    if len(games) < games_count:
        builder.row(
            InlineKeyboardButton(text="➡️", callback_data=GamesCurrentPageCallbackFactory(page=1).pack()),
        )
    await message.answer(text="Игры:", reply_markup=builder.as_markup())


@router.callback_query(GamesCurrentPageCallbackFactory.filter())
async def get_current_page_of_games(
    callback_query: types.CallbackQuery, callback_data: GamesCurrentPageCallbackFactory
):
    uc: GetGamesUseCase = container.resolve(GetGamesUseCase)
    players, players_count = await uc.get_ended_games(
        limit=GAMES_PER_PAGE,
        offset=callback_data.page * GAMES_PER_PAGE,
    )
    builder = _get_games_builder(players, callback_data.page)
    builder.adjust(1)
    buttons = []
    if callback_data.page > 0:
        buttons.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=GamesCurrentPageCallbackFactory(page=callback_data.page - 1).pack(),
            ),
        )
    if players_count > len(players) + callback_data.page * GAMES_PER_PAGE:
        buttons.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=GamesCurrentPageCallbackFactory(page=callback_data.page + 1).pack(),
            )
        )
    if buttons:
        builder.row(*buttons)
    await callback_query.message.edit_text(text="Игры:", reply_markup=builder.as_markup())
    await callback_query.answer()


@router.callback_query(GamesDetailPageCallbackFactory.filter())
async def get_game_detail(callback_query: types.CallbackQuery, callback_data: GamesDetailPageCallbackFactory):
    get_uc: GetGamesUseCase = container.resolve(GetGamesUseCase)
    game = await get_uc.get_game(callback_data.game_id)
    text, _ = _get_game_text_and_keyboard(game=game)
    builder = InlineKeyboardBuilder()
    builder.button(text="Назад", callback_data=GamesCurrentPageCallbackFactory(page=callback_data.page).pack())
    await callback_query.message.edit_text(text=text, reply_markup=builder.as_markup())
    await callback_query.answer()


@router.message(F.text.lower() == "создать игру")
async def create_game(message: types.Message):
    validate_admin(message.from_user.id)
    uc: CreateGameUseCase = container.resolve(CreateGameUseCase)
    now = datetime.datetime.now()
    game = await uc.create_game_in_draft(created_at=now)
    text, kb = _get_game_text_and_keyboard(game=game)
    await message.answer(text=text, reply_markup=kb)


@router.callback_query(GameSeatPlayerRoleCallbackFactory.filter())
async def assign_player_to_seat(callback_query: types.CallbackQuery, callback_data: GameSeatPlayerRoleCallbackFactory):
    validate_admin(callback_query.from_user.id)
    uc: AssignPlayerToSeatUseCase = container.resolve(AssignPlayerToSeatUseCase)
    await uc.assign_player_to_seat(
        game_id=callback_data.game_id,
        seat_number=callback_data.seat_number,
        player_id=callback_data.player_id,
        role=callback_data.role,
    )
    get_uc: GetGamesUseCase = container.resolve(GetGamesUseCase)
    game = await get_uc.get_game(callback_data.game_id)
    text, kb = _get_game_text_and_keyboard(game=game)
    await callback_query.message.edit_text(
        text=text,
        reply_markup=kb,
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
    players, players_count = await uc.get_players(limit=PLAYERS_PER_PAGE, offset=callback_data.page * PLAYERS_PER_PAGE)
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
    get_uc: GetGamesUseCase = container.resolve(GetGamesUseCase)
    game = await get_uc.get_game(callback_data.game_id)
    text, kb = _get_game_text_and_keyboard(game=game)
    await callback_query.message.edit_text(text=text, reply_markup=kb)
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

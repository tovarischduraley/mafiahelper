import math

from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot import keyboards
from bot.auth import is_admin, validate_admin
from bot.filters import (
    ClearStatePlayerDetailCallbackFactory,
    DeletePlayerCallbackFactory,
    PlayerCallbackFactory,
    PlayersCurrentPageCallbackFactory,
    SetPlayerNicknameCallbackFactory,
)
from bot.states import CreatePlayerStates, UpdatePlayerStates
from bot.utils import get_role_emoji, get_team_emoji
from core import Roles, Teams
from dependencies import container
from usecases import (
    CreatePlayerUseCase,
    DeletePlayerUseCase,
    GetPlayerStatsUseCase,
    GetPlayersUseCase,
    SetPlayerNicknameUseCase,
)
from usecases.errors import ValidationError
from usecases.schemas import CreatePlayerSchema, PlayerSchema, PlayerStatsSchema

router = Router()
PLAYERS_PER_PAGE = 10


def _get_players_builder(players: list[PlayerSchema], from_page: int) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for player in players:
        builder.button(
            text=f"{player.nickname}",
            callback_data=PlayerCallbackFactory(player_id=player.id, page=from_page).pack(),
        )
    builder.adjust(2)
    return builder

def _get_player_detail_keyboard(
        current_user_id: int,
        back_button_page: int,
        player_id: int,
        player_detail_message_id: int,
) -> InlineKeyboardMarkup:
    builder = InlineKeyboardBuilder()
    if is_admin(user_id=current_user_id):
        builder.row(
            InlineKeyboardButton(
                text="✍️ Изменить ник",
                callback_data=SetPlayerNicknameCallbackFactory(
                    player_id=player_id,
                    page=back_button_page,
                    message_id=player_detail_message_id,
                ).pack(),
            ),
            InlineKeyboardButton(
                text="🗑️ Удалить",
                callback_data=DeletePlayerCallbackFactory(
                    player_id=player_id,
                    page=back_button_page,
                ).pack(),
            ),
        )
    builder.row(
        InlineKeyboardButton(
            text="Назад",
            callback_data=PlayersCurrentPageCallbackFactory(page=back_button_page).pack(),
        ),
    )
    return builder.as_markup()



@router.message(F.text.lower() == "список игроков")
async def players_list(message: types.Message):
    uc: GetPlayersUseCase = container.resolve(GetPlayersUseCase)
    players, players_count = await uc.get_players(limit=PLAYERS_PER_PAGE)
    builder = _get_players_builder(players, from_page=0)
    builder.adjust(2)
    if not players:
        await message.answer(text="Список игроков пуст.", reply_markup=builder.as_markup())
        return
    if len(players) < players_count:
        builder.row(
            InlineKeyboardButton(text="➡️", callback_data=PlayersCurrentPageCallbackFactory(page=1).pack()),
        )
    await message.answer(text="Игроки:", reply_markup=builder.as_markup())


@router.callback_query(PlayersCurrentPageCallbackFactory.filter())
async def get_current_page_of_players(callback_query: CallbackQuery, callback_data: PlayersCurrentPageCallbackFactory):
    uc: GetPlayersUseCase = container.resolve(GetPlayersUseCase)
    players, players_count = await uc.get_players(limit=PLAYERS_PER_PAGE, offset=callback_data.page * PLAYERS_PER_PAGE)
    if not players_count:
        await callback_query.message.edit_text(text="Список игроков пуст.")
        await callback_query.answer()
        return
    if callback_data.page > math.ceil(players_count / PLAYERS_PER_PAGE - 1):
        callback_data.page = math.ceil(players_count / PLAYERS_PER_PAGE - 1)
        players, players_count = await uc.get_players(limit=PLAYERS_PER_PAGE, offset=callback_data.page)

    builder = _get_players_builder(players, callback_data.page)
    builder.adjust(2)
    buttons = []
    if callback_data.page > 0:
        buttons.append(
            InlineKeyboardButton(
                text="⬅️",
                callback_data=PlayersCurrentPageCallbackFactory(page=callback_data.page - 1).pack(),
            ),
        )
    if players_count > len(players) + callback_data.page * PLAYERS_PER_PAGE:
        buttons.append(
            InlineKeyboardButton(
                text="➡️",
                callback_data=PlayersCurrentPageCallbackFactory(page=callback_data.page + 1).pack(),
            )
        )
    if buttons:
        builder.row(*buttons)
    await callback_query.message.edit_text(text="Игроки:", reply_markup=builder.as_markup())
    await callback_query.answer()


def _get_player_stats_text(player: PlayerStatsSchema) -> str:
    games_count_total_text = f"{player.games_count_total}"
    win_percent_general_text = f"{player.win_percent_general}%" if player.win_percent_general is not None else "--"
    win_percent_black_team_text = (
        f"{player.win_percent_black_team}%" if player.win_percent_black_team is not None else "--"
    )
    win_percent_red_team_text = f"{player.win_percent_red_team}%" if player.win_percent_red_team is not None else "--"
    win_percent_as_civilian_text = (
        f"{player.win_percent_as_civilian}%" if player.win_percent_as_civilian is not None else "--"
    )
    win_percent_as_mafia_text = f"{player.win_percent_as_mafia}%" if player.win_percent_as_mafia is not None else "--"
    win_percent_as_don_text = f"{player.win_percent_as_don}%" if player.win_percent_as_don is not None else "--"
    win_percent_as_sheriff_text = (
        f"{player.win_percent_as_sheriff}%" if player.win_percent_as_sheriff is not None else "--"
    )
    best_move_text = (
        (
            f"\n\n*Лучший ход*:\n"
            f"Всего: {player.best_move_count_total}\n"
            f"0 / 3 черных: {player.zero_mafia_best_move_count}\n"
            f"1 / 3 черных: {player.one_mafia_best_move_count}\n"
            f"2 / 3 черных: {player.two_mafia_best_move_count}\n"
            f"3 / 3 черных: {player.three_mafia_best_move_count}"
        )
        if player.best_move_count_total
        else ""
    )

    return (
        f"*{player.nickname}*\n"
        f"{player.fio}\n\n"
        f"Всего игр: {games_count_total_text}\n"
        f"Убит в первую ночь: {player.first_killed_count}\n"
        f"Общий процент побед: "
        f"{win_percent_general_text} ({player.won_games_count_total} / {games_count_total_text})\n\n"
        f"{get_team_emoji(Teams.BLACK)}\t Черная команда: "
        f"{win_percent_black_team_text} ({player.won_games_count_black_team} / {player.games_count_black_team})\n"
        f"{get_team_emoji(Teams.RED)}\t Красная команда: "
        f"{win_percent_red_team_text} ({player.won_games_count_red_team} / {player.games_count_red_team})\n\n"
        f"{get_role_emoji(Roles.CIVILIAN)}\t Мирный житель: "
        f"{win_percent_as_civilian_text} ({player.won_games_count_as_civilian} / {player.games_count_as_civilian})\n"
        f"{get_role_emoji(Roles.MAFIA)}\t Мафия: "
        f"{win_percent_as_mafia_text} ({player.won_games_count_as_mafia} / {player.games_count_as_mafia})\n"
        f"{get_role_emoji(Roles.DON)}\t Дон: "
        f"{win_percent_as_don_text} ({player.won_games_count_as_don} / {player.games_count_as_don})\n"
        f"{get_role_emoji(Roles.SHERIFF)}\t Шериф: "
        f"{win_percent_as_sheriff_text} ({player.won_games_count_as_sheriff} / {player.games_count_as_sheriff})"
        f"{best_move_text}"
    )


@router.callback_query(PlayerCallbackFactory.filter())
async def player_detail(callback_query: CallbackQuery, callback_data: PlayerCallbackFactory):
    uc: GetPlayerStatsUseCase = container.resolve(GetPlayerStatsUseCase)
    player_stats = await uc.get_player_stats(player_id=callback_data.player_id)
    await callback_query.message.edit_text(
        text=_get_player_stats_text(player_stats),
        reply_markup=_get_player_detail_keyboard(
            current_user_id=callback_query.from_user.id,
            player_id=callback_data.player_id,
            back_button_page=callback_data.page,
            player_detail_message_id=callback_query.message.message_id,
        ),
        parse_mode=ParseMode.MARKDOWN,
    )
    await callback_query.answer()


@router.callback_query(DeletePlayerCallbackFactory.filter())
async def delete_player(callback_query: CallbackQuery, callback_data: DeletePlayerCallbackFactory):
    validate_admin(callback_query.from_user.id)
    uc: DeletePlayerUseCase = container.resolve(DeletePlayerUseCase)
    try:
        await uc.delete_player(player_id=callback_data.player_id)
    except ValidationError as e:
        await callback_query.answer(text=str(e))
    else:
        await callback_query.answer(text="Player deleted")
        await get_current_page_of_players(
            callback_query=callback_query, callback_data=PlayersCurrentPageCallbackFactory(page=callback_data.page)
        )


@router.callback_query(SetPlayerNicknameCallbackFactory.filter())
async def set_player_nickname_button(
    callback_query: CallbackQuery,
    callback_data: SetPlayerNicknameCallbackFactory,
    state: FSMContext,
):
    validate_admin(callback_query.from_user.id)
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Назад",
                    callback_data=ClearStatePlayerDetailCallbackFactory(
                        player_id=callback_data.player_id,
                        page=callback_data.page,
                    ).pack()
                )
            ]
        ]
    )
    await callback_query.message.edit_text("Введите новый ник игрока", reply_markup=kb)
    await state.set_state(UpdatePlayerStates.setting_nickname)
    await state.update_data(player_data=callback_data)

@router.callback_query(ClearStatePlayerDetailCallbackFactory.filter())
async def clear_state(
    callback_query: CallbackQuery,
    callback_data: ClearStatePlayerDetailCallbackFactory,
    state: FSMContext,
):
    await state.clear()
    return await player_detail(
        callback_query=callback_query,
        callback_data=PlayerCallbackFactory(player_id=callback_data.player_id, page=callback_data.page),
    )

@router.message(UpdatePlayerStates.setting_nickname, F.text)
async def set_player_nickname(message: types.Message, state: FSMContext):
    validate_admin(message.from_user.id)
    nickname_uc: SetPlayerNicknameUseCase = container.resolve(SetPlayerNicknameUseCase)
    player_stats_uc: GetPlayerStatsUseCase = container.resolve(GetPlayerStatsUseCase)
    data: dict[str, SetPlayerNicknameCallbackFactory] = await state.get_data()
    await nickname_uc.set_player_nickname(player_id=data["player_data"].player_id, nickname=message.text)
    player_with_stats = await player_stats_uc.get_player_stats(player_id=data["player_data"].player_id)
    await state.clear()
    await message.bot.edit_message_text(
        chat_id=message.chat.id,
        message_id=data["player_data"].message_id,
        text=_get_player_stats_text(player=player_with_stats),
        reply_markup=_get_player_detail_keyboard(
            current_user_id=message.from_user.id,
            back_button_page=data["player_data"].page,
            player_id=data["player_data"].player_id,
            player_detail_message_id=data["player_data"].message_id,
        ),
        parse_mode=ParseMode.MARKDOWN,
    )


@router.message(F.text.lower() == "создать игрока")
async def create_player(message: types.Message, state: FSMContext):
    validate_admin(message.from_user.id)
    await message.answer("Введите ФИО игрока")
    await state.set_state(CreatePlayerStates.waiting_fio)


@router.message(CreatePlayerStates.waiting_fio, F.text)
async def process_player_fio(message: types.Message, state: FSMContext):
    validate_admin(message.from_user.id)
    await state.update_data(fio=message.text)
    await message.answer("Введите ник игрока")
    await state.set_state(CreatePlayerStates.waiting_nickname)


@router.message(CreatePlayerStates.waiting_nickname, F.text)
async def process_player_nickname(message: types.Message, state: FSMContext):
    validate_admin(message.from_user.id)
    await state.update_data(nickname=message.text)
    uc: CreatePlayerUseCase = container.resolve(CreatePlayerUseCase)
    player_data = await state.get_data()
    await uc.create_player(CreatePlayerSchema(**player_data))
    await message.answer(
        text=f"Вы создали игрока!\n\nИмя: {player_data['fio']}\nПсевдоним: {player_data['nickname']}",
        reply_markup=keyboards.admin_kb,
    )
    await state.clear()

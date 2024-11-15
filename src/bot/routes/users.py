from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.utils.keyboard import InlineKeyboardBuilder

from bot import keyboards
from bot.filters import UserCallbackFactory, UsersCurrentPageCallbackFactory
from bot.states import CreateUserStates
from bot.utils import get_role_emoji, get_team_emoji
from core import Roles, Teams
from dependencies import container
from usecases import CreateUserUseCase, GetUserStatsUseCase, GetUsersUseCase
from usecases.schemas import CreateUserSchema, UserSchema, UserStatsSchema

router = Router()
USERS_PER_PAGE = 10


def _get_users_builder(users: list[UserSchema], from_page: int) -> InlineKeyboardBuilder:
    builder = InlineKeyboardBuilder()
    for user in users:
        builder.button(
            text=f"{user.nickname}",
            callback_data=UserCallbackFactory(user_id=user.id, users_page=from_page).pack(),
        )
    builder.adjust(1)
    return builder


@router.message(F.text.lower() == "список игроков")
async def players_list(message: types.Message):
    uc: GetUsersUseCase = container.resolve(GetUsersUseCase)
    users = await uc.get_users(limit=USERS_PER_PAGE)
    users_count = await uc.get_users_count()
    builder = _get_users_builder(users, from_page=0)
    builder.adjust(1)
    if not users:
        await message.answer(text="Список игроков пуст.", reply_markup=builder.as_markup())
        return
    if len(users) < users_count:
        builder.row(
            InlineKeyboardButton(text="➡️", callback_data="next:1"),
        )
    await message.answer(text="Игроки:", reply_markup=builder.as_markup())


@router.callback_query(UsersCurrentPageCallbackFactory.filter())
async def get_current_page_of_users(callback_query: CallbackQuery, callback_data: UsersCurrentPageCallbackFactory):
    uc: GetUsersUseCase = container.resolve(GetUsersUseCase)
    users = await uc.get_users(limit=USERS_PER_PAGE, offset=callback_data.page * USERS_PER_PAGE)
    users_count = await uc.get_users_count()
    builder = _get_users_builder(users, callback_data.page)
    builder.adjust(2)
    btns = []
    if callback_data.page > 0:
        btns.append(InlineKeyboardButton(text="⬅️", callback_data=f"prev:{callback_data.page - 1}"))
    if users_count > len(users) + callback_data.page * USERS_PER_PAGE:
        btns.append(InlineKeyboardButton(text="➡️", callback_data=f"next:{callback_data.page + 1}"))
    if btns:
        builder.row(*btns)
    await callback_query.message.edit_text(text="Игроки:", reply_markup=builder.as_markup())
    await callback_query.answer()


@router.callback_query(F.data.startswith("next:"))
async def get_next_users(callback_query: CallbackQuery):
    current_page = int(callback_query.data.split(":")[-1])
    uc: GetUsersUseCase = container.resolve(GetUsersUseCase)
    users = await uc.get_users(limit=USERS_PER_PAGE, offset=current_page * USERS_PER_PAGE)
    users_count = await uc.get_users_count()
    builder = _get_users_builder(users, current_page)
    builder.adjust(2)
    if users_count > len(users) + current_page * USERS_PER_PAGE:
        builder.row(
            InlineKeyboardButton(text="⬅️", callback_data=f"prev:{current_page - 1}"),
            InlineKeyboardButton(text="➡️", callback_data=f"next:{current_page + 1}"),
        )
    else:
        builder.row(InlineKeyboardButton(text="⬅️", callback_data=f"prev:{current_page - 1}"))
    await callback_query.message.edit_text(text="Игроки:", reply_markup=builder.as_markup())
    await callback_query.answer()


@router.callback_query(F.data.startswith("prev:"))
async def get_prev_users(callback_query: CallbackQuery):
    current_page = int(callback_query.data.split(":")[-1])
    uc: GetUsersUseCase = container.resolve(GetUsersUseCase)
    users = await uc.get_users(limit=USERS_PER_PAGE, offset=current_page * USERS_PER_PAGE)
    builder = _get_users_builder(users, current_page)
    builder.adjust(2)
    if len(users) + current_page * USERS_PER_PAGE > USERS_PER_PAGE:
        builder.row(
            InlineKeyboardButton(text="⬅️", callback_data=f"prev:{current_page - 1}"),
            InlineKeyboardButton(text="➡️", callback_data=f"next:{current_page + 1}"),
        )
    else:
        builder.row(InlineKeyboardButton(text="➡️", callback_data=f"next:{current_page + 1}"))
    await callback_query.message.edit_text(text="Игроки:", reply_markup=builder.as_markup())
    await callback_query.answer()


def _get_user_stats_text(user: UserStatsSchema) -> str:
    games_count_total_text = f"{user.games_count_total}"
    win_percent_general_text = f"{user.win_percent_general}%" if user.win_percent_general is not None else "--"
    win_percent_black_team_text = f"{user.win_percent_black_team}%" if user.win_percent_black_team is not None else "--"
    win_percent_red_team_text = f"{user.win_percent_red_team}%" if user.win_percent_red_team is not None else "--"
    win_percent_as_civilian_text = (
        f"{user.win_percent_as_civilian}%" if user.win_percent_as_civilian is not None else "--"
    )
    win_percent_as_mafia_text = f"{user.win_percent_as_mafia}%" if user.win_percent_as_mafia is not None else "--"
    win_percent_as_don_text = f"{user.win_percent_as_don}%" if user.win_percent_as_don is not None else "--"
    win_percent_as_sheriff_text = f"{user.win_percent_as_sheriff}%" if user.win_percent_as_sheriff is not None else "--"
    return (
        f"*{user.nickname}*\n"
        f"{user.fio}\n\n"
        f"Всего игр: {games_count_total_text}\n"
        f"Общий процент побед: {win_percent_general_text}\n\n"
        f"{get_team_emoji(Teams.BLACK)}\t Процент побед в черной команде: {win_percent_black_team_text}\n"
        f"{get_team_emoji(Teams.RED)}\t Процент побед в красной команде: {win_percent_red_team_text}\n\n"
        f"{get_role_emoji(Roles.CIVILIAN)}\t Процент побед за мирного жителя: {win_percent_as_civilian_text}\n"
        f"{get_role_emoji(Roles.MAFIA)}\t Процент побед за мафию: {win_percent_as_mafia_text}\n"
        f"{get_role_emoji(Roles.DON)}\t Процент побед за дона: {win_percent_as_don_text}\n"
        f"{get_role_emoji(Roles.SHERIFF)}\t Процент побед за шерифа: {win_percent_as_sheriff_text}\n"
    )


@router.callback_query(UserCallbackFactory.filter())
async def user_detail(callback_query: CallbackQuery, callback_data: UserCallbackFactory):
    uc: GetUserStatsUseCase = container.resolve(GetUserStatsUseCase)
    user_stats = await uc.get_user_stats(user_id=callback_data.user_id)
    kb = InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="Назад",
                    callback_data=UsersCurrentPageCallbackFactory(page=callback_data.users_page).pack()
                )
            ],
        ]
    )
    await callback_query.message.edit_text(
        text=_get_user_stats_text(user_stats), reply_markup=kb, parse_mode=ParseMode.MARKDOWN
    )
    await callback_query.answer()


@router.message(F.text.lower() == "создать игрока")
async def create_player(message: types.Message, state: FSMContext):
    await message.answer("Введите ФИО игрока")
    await state.set_state(CreateUserStates.waiting_fio)


@router.message(CreateUserStates.waiting_fio, F.text)
async def process_user_fio(message: types.Message, state: FSMContext):
    await state.update_data(fio=message.text)
    await message.answer("Введите игровой псевдоним игрока")
    await state.set_state(CreateUserStates.waiting_nickname)


@router.message(CreateUserStates.waiting_nickname, F.text)
async def process_user_nickname(message: types.Message, state: FSMContext):
    await state.update_data(nickname=message.text)
    uc: CreateUserUseCase = container.resolve(CreateUserUseCase)
    user_data = await state.get_data()
    await uc.create_user(CreateUserSchema(**user_data))
    await message.answer(
        text=f"Вы создали игрока!\n\nИмя: {user_data["fio"]}\nПсевдоним: {user_data["nickname"]}",
        reply_markup=keyboards.menu,
    )
    await state.clear()

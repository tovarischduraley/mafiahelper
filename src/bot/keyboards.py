from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Создать игрока"), KeyboardButton(text="Список игроков")],
        [KeyboardButton(text="Создать игру")],
    ],
    resize_keyboard=True,
)

create_game_inline_keyboard = InlineKeyboardMarkup(
    inline_keyboard=[
        [InlineKeyboardButton(text="игроки", callback_data="game_players")]
    ]
)

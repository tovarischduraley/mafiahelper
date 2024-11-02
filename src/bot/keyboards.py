from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Создать игрока")],
        [KeyboardButton(text="Список игроков"), KeyboardButton(text="Создать игру")],
    ],
    resize_keyboard=True,
)

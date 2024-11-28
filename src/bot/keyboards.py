from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

admin_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Список игроков")],
        [KeyboardButton(text="Сгенерировать рассадку")],
        [KeyboardButton(text="Создать игрока"), KeyboardButton(text="Создать игру")],
    ],
    resize_keyboard=True,
)

user_kb = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Список игроков")],
    ],
    resize_keyboard=True,
)

from aiogram.types import KeyboardButton, ReplyKeyboardMarkup

menu = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Список игроков")],
        [KeyboardButton(text="Сгенерировать рассадку")],
        [KeyboardButton(text="Создать игрока"), KeyboardButton(text="Создать игру")],
    ],
    resize_keyboard=True,
)

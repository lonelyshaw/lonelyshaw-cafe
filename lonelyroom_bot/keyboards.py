from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


MENU_ROOM = "🏡 Моя комната"
MENU_BOOK = "📖 Книга обо мне"
MENU_DAILY = "🌙 Вопрос дня"
MENU_MOMENT = "✨ Сохранить момент"
MENU_LETTERS = "💌 Письма"
MENU_EVENING = "☕ Собери мне вечер"
MENU_TALK = "🤍 Поговорить"

BACK = "⬅️ В меню"

BOOK_ADD = "➕ Добавить страницу"
BOOK_READ = "📚 Последние страницы"

LETTER_WRITE = "✍️ Написать письмо"
LETTER_READ = "📬 Последние письма"


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=MENU_ROOM), KeyboardButton(text=MENU_BOOK)],
            [KeyboardButton(text=MENU_DAILY), KeyboardButton(text=MENU_MOMENT)],
            [KeyboardButton(text=MENU_LETTERS), KeyboardButton(text=MENU_EVENING)],
            [KeyboardButton(text=MENU_TALK)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите уголок комнаты",
    )


def book_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=BOOK_ADD), KeyboardButton(text=BOOK_READ)],
            [KeyboardButton(text=BACK)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Книга обо мне",
    )


def letters_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=LETTER_WRITE), KeyboardButton(text=LETTER_READ)],
            [KeyboardButton(text=BACK)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Письма себе",
    )


def back_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BACK)]],
        resize_keyboard=True,
        input_field_placeholder="Можно вернуться в меню",
    )

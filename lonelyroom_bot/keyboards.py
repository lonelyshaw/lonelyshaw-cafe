from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


MENU_ROOM = "🏡 Моя комната"
MENU_BOOK = "📖 Книга обо мне"
MENU_DAILY = "🌙 Вопрос дня"
MENU_MOMENT = "🕯 Моменты"
MENU_LETTERS = "💌 Письмо себе"
MENU_MEDIA = "🎬 Медиа"

OLD_MENU_MOMENT = "✨ Сохранить момент"
OLD_MENU_LETTERS = "💌 Письма"
MENU_EVENING = "☕ Собери мне вечер"
MENU_TALK = "🤍 Поговорить"

BACK = "⬅️ В меню"

BOOK_ADD = "➕ Добавить страницу"
BOOK_READ = "📚 Последние страницы"

LETTER_WRITE = "✍️ Написать письмо"
LETTER_READ = "📬 Последние письма"

MEDIA_BOOKS = "📚 Книги"
MEDIA_MOVIES = "🎬 Фильмы"
MEDIA_MUSIC = "🎵 Музыка"


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=MENU_ROOM), KeyboardButton(text=MENU_BOOK)],
            [KeyboardButton(text=MENU_DAILY), KeyboardButton(text=MENU_MOMENT)],
            [KeyboardButton(text=MENU_LETTERS), KeyboardButton(text=MENU_MEDIA)],
        ],
        is_persistent=True,
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


def media_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=MEDIA_BOOKS), KeyboardButton(text=MEDIA_MOVIES)],
            [KeyboardButton(text=MEDIA_MUSIC)],
            [KeyboardButton(text=BACK)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Медиа для вечера",
    )


def back_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BACK)]],
        resize_keyboard=True,
        input_field_placeholder="Можно вернуться в меню",
    )

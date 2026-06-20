from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


MENU_ROOM = "🏡 Моя комната"
MENU_BOOK = "📖 Книга обо мне"
MENU_DAILY = "🌙 Вопрос дня"
MENU_MOOD = "🌧 Настроение"
MENU_MOMENT = "🕯 Моменты"
MENU_LETTERS = "💌 Письмо себе"
MENU_PETS = "🦊 Питомцы"
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

MOOD_CALM = "спокойно"
MOOD_ANXIOUS = "тревожно"
MOOD_SAD = "грустно"
MOOD_COZY = "уютно"
MOOD_TIRED = "устало"
MOOD_HAPPY = "радостно"

MOODS = (
    MOOD_CALM,
    MOOD_ANXIOUS,
    MOOD_SAD,
    MOOD_COZY,
    MOOD_TIRED,
    MOOD_HAPPY,
)


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=MENU_ROOM), KeyboardButton(text=MENU_BOOK)],
            [KeyboardButton(text=MENU_DAILY), KeyboardButton(text=MENU_MOOD)],
            [KeyboardButton(text=MENU_MOMENT), KeyboardButton(text=MENU_LETTERS)],
            [KeyboardButton(text=MENU_PETS), KeyboardButton(text=MENU_MEDIA)],
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


def mood_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=MOOD_CALM), KeyboardButton(text=MOOD_ANXIOUS)],
            [KeyboardButton(text=MOOD_SAD), KeyboardButton(text=MOOD_COZY)],
            [KeyboardButton(text=MOOD_TIRED), KeyboardButton(text=MOOD_HAPPY)],
            [KeyboardButton(text=BACK)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Выберите настроение дня",
    )


def back_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BACK)]],
        resize_keyboard=True,
        input_field_placeholder="Можно вернуться в меню",
    )

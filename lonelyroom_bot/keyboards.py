from aiogram.types import KeyboardButton, ReplyKeyboardMarkup


MENU_ROOM = "🏡 Моя комната"
MENU_BOOK = "📖 Книга обо мне"
MENU_DAILY = "🌙 Вопрос дня"
MENU_MOOD = "🌧 Настроение"
MENU_MOMENT = "🕯 Моменты"
MENU_LETTERS = "💌 Письмо себе"
MENU_PETS = "🦊 Питомцы"
MENU_MIRROR = "🪞 Зеркало"
MENU_ARCHIVE = "🧳 Архив"
MENU_SETTINGS = "⚙️ Настройки"
MENU_FRIEND_ROOMS = "🚪 Комнаты друзей"
MENU_DOOR_NOTES = "💌 Записки у двери"
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

ROOM_CREATE_NICKNAME = "Создать ник комнаты"
ROOM_PRIVACY = "🔒 Приватность комнаты"

GUEST_LEAVE_NOTE = "💌 Оставить записку"
GUEST_LEAVE_LIGHT = "✨ Оставить огонёк"

PRIVACY_ONLY_ME = "🔒 Только я"
PRIVACY_BY_NICKNAME = "👥 Только друзья по нику"
PRIVACY_PUBLIC = "🌙 Открыта всем по нику"

PRIVACY_OPTIONS = (
    PRIVACY_ONLY_ME,
    PRIVACY_BY_NICKNAME,
    PRIVACY_PUBLIC,
)

PRIVACY_VALUES = {
    PRIVACY_ONLY_ME: "private",
    PRIVACY_BY_NICKNAME: "nickname",
    PRIVACY_PUBLIC: "public",
}

PRIVACY_LABELS = {value: label for label, value in PRIVACY_VALUES.items()}

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
            [KeyboardButton(text=MENU_MIRROR), KeyboardButton(text=MENU_ARCHIVE)],
            [KeyboardButton(text=MENU_FRIEND_ROOMS), KeyboardButton(text=MENU_DOOR_NOTES)],
            [KeyboardButton(text=MENU_SETTINGS)],
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


def room_menu(has_nickname: bool) -> ReplyKeyboardMarkup:
    keyboard = []
    if not has_nickname:
        keyboard.append([KeyboardButton(text=ROOM_CREATE_NICKNAME)])
    else:
        keyboard.append([KeyboardButton(text=ROOM_CREATE_NICKNAME), KeyboardButton(text=ROOM_PRIVACY)])
    keyboard.append([KeyboardButton(text=MENU_DOOR_NOTES), KeyboardButton(text=BACK)])

    return ReplyKeyboardMarkup(
        keyboard=keyboard,
        resize_keyboard=True,
        input_field_placeholder="Моя комната",
    )


def settings_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=ROOM_CREATE_NICKNAME)],
            [KeyboardButton(text=ROOM_PRIVACY)],
            [KeyboardButton(text=BACK)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Настройки комнаты",
    )


def privacy_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=PRIVACY_ONLY_ME)],
            [KeyboardButton(text=PRIVACY_BY_NICKNAME)],
            [KeyboardButton(text=PRIVACY_PUBLIC)],
            [KeyboardButton(text=BACK)],
        ],
        resize_keyboard=True,
        input_field_placeholder="Приватность комнаты",
    )


def guest_room_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[
            [KeyboardButton(text=GUEST_LEAVE_NOTE)],
            [KeyboardButton(text=GUEST_LEAVE_LIGHT)],
            [KeyboardButton(text=BACK)],
        ],
        resize_keyboard=True,
        input_field_placeholder="У двери комнаты",
    )


def back_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text=BACK)]],
        resize_keyboard=True,
        input_field_placeholder="Можно вернуться в меню",
    )

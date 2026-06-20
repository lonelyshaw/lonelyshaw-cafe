from datetime import date
from html import escape
from random import choice
import re

from aiogram import F, Router
from aiogram.filters import Command, CommandStart, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.types import Message

from lonelyroom_bot.conversation import build_conversation_reply
from lonelyroom_bot.database import Database
from lonelyroom_bot.keyboards import (
    BACK,
    BOOK_ADD,
    BOOK_READ,
    MEDIA_BOOKS,
    MEDIA_MOVIES,
    MEDIA_MUSIC,
    MOODS,
    GUEST_LEAVE_LIGHT,
    GUEST_LEAVE_NOTE,
    LETTER_READ,
    LETTER_WRITE,
    MENU_BOOK,
    MENU_DAILY,
    MENU_DOOR_NOTES,
    MENU_EVENING,
    MENU_LETTERS,
    MENU_ARCHIVE,
    MENU_FRIEND_ROOMS,
    MENU_MEDIA,
    MENU_MIRROR,
    MENU_MOMENT,
    MENU_MOOD,
    MENU_PETS,
    MENU_ROOM,
    MENU_SETTINGS,
    MENU_TALK,
    OLD_MENU_LETTERS,
    OLD_MENU_MOMENT,
    PRIVACY_BY_NICKNAME,
    PRIVACY_LABELS,
    PRIVACY_OPTIONS,
    PRIVACY_VALUES,
    ROOM_CREATE_NICKNAME,
    ROOM_PRIVACY,
    back_menu,
    book_menu,
    guest_room_menu,
    letters_menu,
    main_menu,
    media_menu,
    mood_menu,
    privacy_menu,
    room_menu,
    settings_menu,
)
from lonelyroom_bot.pets import PETS, action_total
from lonelyroom_bot.states import (
    BookForm,
    DailyQuestionForm,
    FriendRoomForm,
    LetterForm,
    MirrorForm,
    MomentForm,
    RoomNicknameForm,
    RoomNoteForm,
    TalkForm,
)
from lonelyroom_bot.texts import (
    EMPTY_TEXT,
    EVENING_RECIPES,
    MENU_TEXT,
    SMALL_DISCOVERIES,
    WELCOME_TEXT,
    question_for_day,
    trim_text,
)


router = Router(name="lonelyroom")
ROOM_NICKNAME_PATTERN = re.compile(r"^[A-Za-z0-9_]{3,20}$")

NAVIGATION_TEXTS = {
    MENU_ROOM,
    MENU_BOOK,
    MENU_DAILY,
    MENU_MOOD,
    MENU_MOMENT,
    MENU_LETTERS,
    MENU_ARCHIVE,
    MENU_DOOR_NOTES,
    MENU_FRIEND_ROOMS,
    MENU_PETS,
    MENU_MEDIA,
    MENU_MIRROR,
    MENU_SETTINGS,
    MENU_EVENING,
    MENU_TALK,
    OLD_MENU_MOMENT,
    OLD_MENU_LETTERS,
    BOOK_ADD,
    BOOK_READ,
    LETTER_WRITE,
    LETTER_READ,
    GUEST_LEAVE_NOTE,
    GUEST_LEAVE_LIGHT,
    ROOM_CREATE_NICKNAME,
    ROOM_PRIVACY,
    *PRIVACY_OPTIONS,
    MEDIA_BOOKS,
    MEDIA_MOVIES,
    MEDIA_MUSIC,
    *MOODS,
}


async def get_user_id(message: Message, db: Database) -> int:
    if message.from_user is None:
        raise RuntimeError("Сообщение без пользователя")

    return await db.ensure_user(
        telegram_id=message.from_user.id,
        username=message.from_user.username,
        first_name=message.from_user.first_name,
    )


def clean_text(message: Message) -> str | None:
    if message.text is None:
        return None

    text = message.text.strip()
    return text or None


def is_navigation_text(text: str) -> bool:
    return text in NAVIGATION_TEXTS


def format_short_list(rows: list, field: str = "text") -> str:
    if not rows:
        return EMPTY_TEXT

    items = []
    for index, row in enumerate(rows, start=1):
        value = escape(trim_text(str(row[field]), 140))
        items.append(f"{index}. {value}")
    return "\n\n".join(items)


async def answer_conversation(
    message: Message,
    db: Database,
    user_id: int,
    user_text: str,
    *,
    in_talk_mode: bool,
) -> None:
    history = await db.latest_conversation_messages(user_id)
    reply = build_conversation_reply(user_text, history)

    await db.add_conversation_message(user_id, "user", user_text)
    await db.add_conversation_message(user_id, "bot", reply.text)

    await message.answer(
        reply.text,
        reply_markup=back_menu() if in_talk_mode else main_menu(),
    )


def important_action_total(stats: dict[str, int]) -> int:
    return action_total(stats)


def room_atmosphere(stats: dict[str, int]) -> str:
    total = important_action_total(stats)
    if total <= 2:
        return "Комната ещё почти пустая, но в ней уже есть место для тебя."
    if total <= 5:
        return "В комнате стало чуть теплее. Где-то горит маленький свет."
    if total < 10:
        return "На полке появляются первые следы дней: страницы, письма и моменты."
    return "Это место уже похоже на дом."


def room_light(stats: dict[str, int]) -> str:
    total = important_action_total(stats)
    if total <= 2:
        return "сумерки"
    if total <= 5:
        return "маленькая лампа"
    if total < 10:
        return "тёплый вечерний свет"
    return "домашний свет"


def room_shelf(stats: dict[str, int]) -> str:
    total_saved = stats["book"] + stats["moments"] + stats["letters"] + stats["answers"]
    if total_saved == 0:
        return "пустая полка"
    if total_saved <= 5:
        return "первые записи"
    if total_saved <= 10:
        return "книги, письма и моменты"
    return "целая маленькая история"


def nearby_pet_name(pet_rows: list) -> str:
    if not pet_rows:
        return "пока тихо"

    pet_codes = {str(row["pet_code"]) for row in pet_rows}
    for pet in PETS:
        if pet.code in pet_codes:
            return pet.title

    return str(pet_rows[0]["name"]).split(" ", 1)[-1]


def archive_block(title: str, rows: list, field: str = "text") -> str:
    if not rows:
        return f"<b>{title}</b>\nздесь пока тихо."

    items = []
    for index, row in enumerate(rows, start=1):
        value = escape(trim_text(str(row[field]), 110))
        items.append(f"{index}. {value}")
    return f"<b>{title}</b>\n" + "\n".join(items)


def daily_answers_block(rows: list) -> str:
    if not rows:
        return "<b>🌙 Ответы дня</b>\nздесь пока тихо."

    items = []
    for index, row in enumerate(rows, start=1):
        question = escape(trim_text(str(row["question"]), 70))
        answer = escape(trim_text(str(row["answer"]), 100))
        items.append(f"{index}. {question}\n{answer}")
    return "<b>🌙 Ответы дня</b>\n" + "\n\n".join(items)


def normalize_room_nickname(value: str) -> str:
    nickname = value.strip()
    if nickname.startswith("@"):
        nickname = nickname[1:]
    return nickname.lower()


def is_valid_room_nickname(nickname: str) -> bool:
    return bool(ROOM_NICKNAME_PATTERN.fullmatch(nickname))


def guest_author_label(profile) -> str:
    if profile and profile["room_nickname"]:
        return f"@{profile['room_nickname']}"
    return "от гостя без имени"


async def notify_room_updates(message: Message, db: Database, user_id: int) -> None:
    notes = await db.unread_room_notes(user_id)
    if notes:
        for row in notes:
            author = f"@{row['guest_room_nickname']}" if row["guest_room_nickname"] else "от гостя без имени"
            await message.answer(
                "💌 У двери появилась новая записка.\n\n"
                f"“{escape(trim_text(str(row['text']), 500))}”\n\n"
                f"От: {escape(author)}",
                reply_markup=main_menu(),
            )
        await db.mark_room_notes_read(user_id)

    lights_count = await db.unseen_room_lights_count(user_id)
    if lights_count:
        await message.answer(
            "✨ Кто-то оставил маленький огонёк у твоей двери.",
            reply_markup=main_menu(),
        )
        await db.mark_room_lights_seen(user_id)


async def guest_room_text(db: Database, owner_id: int, nickname: str) -> str:
    await db.unlock_eligible_pets(owner_id)
    stats = await db.room_stats(owner_id)
    pets_rows = await db.latest_pets(owner_id)
    lights_count = await db.room_light_count(owner_id)
    items_count = stats["book"] + stats["moments"] + stats["pets"]

    return (
        f"🏡 <b>Комната @{escape(nickname)}</b>\n\n"
        "🌧 За окном: тихий дождь\n"
        f"🕯 Свет: {escape(room_light(stats))}\n"
        f"🦊 Рядом: {escape(nearby_pet_name(pets_rows))}\n"
        f"🎒 Предметов: {items_count}\n"
        f"📖 Страниц: {stats['book']}\n"
        f"🕯 Моментов: {stats['moments']}\n"
        f"✨ Огоньков у двери: {lights_count}\n\n"
        "“каждый человек — это целая комната.”"
    )


async def maybe_unlock_pet(message: Message, db: Database, user_id: int) -> bool:
    unlocked_pets = await db.unlock_eligible_pets(user_id)
    if not unlocked_pets:
        return False

    for pet in unlocked_pets:
        await message.answer(
            f"{pet.emoji} В комнате кто-то появился.\n\n"
            f"{pet.arrival_text}",
            reply_markup=main_menu(),
        )
    return True


async def maybe_send_small_discovery(message: Message, db: Database, user_id: int) -> None:
    stats = await db.room_stats(user_id)
    total = important_action_total(stats)

    if total > 0 and total % 3 == 0:
        discovery = SMALL_DISCOVERIES[(total // 3 - 1) % len(SMALL_DISCOVERIES)]
        await message.answer(discovery, reply_markup=main_menu())


async def after_important_action(message: Message, db: Database, user_id: int) -> None:
    if await maybe_unlock_pet(message, db, user_id):
        return

    await maybe_send_small_discovery(message, db, user_id)


@router.message(CommandStart())
async def start(message: Message, state: FSMContext, db: Database) -> None:
    await state.clear()
    user_id = await get_user_id(message, db)
    profile = await db.room_profile(user_id)
    text = WELCOME_TEXT
    if profile and not profile["room_nickname"]:
        text += "\n\nМожно создать ник комнаты.\nТак друзья смогут найти твою дверь."
    await message.answer(text, reply_markup=main_menu())
    await notify_room_updates(message, db, user_id)


@router.message(Command("menu"))
async def menu(message: Message, state: FSMContext, db: Database) -> None:
    await state.clear()
    user_id = await get_user_id(message, db)
    await message.answer(MENU_TEXT, reply_markup=main_menu())
    await notify_room_updates(message, db, user_id)


@router.message(F.text == BACK)
async def back_to_menu(message: Message, state: FSMContext, db: Database) -> None:
    await state.clear()
    user_id = await get_user_id(message, db)
    await message.answer(MENU_TEXT, reply_markup=main_menu())
    await notify_room_updates(message, db, user_id)


@router.message(StateFilter(None), F.text == MENU_ROOM)
async def show_room(message: Message, db: Database) -> None:
    user_id = await get_user_id(message, db)
    await db.unlock_eligible_pets(user_id)
    stats = await db.room_stats(user_id)
    pets_rows = await db.latest_pets(user_id)
    profile = await db.room_profile(user_id)
    nickname = f"@{profile['room_nickname']}" if profile and profile["room_nickname"] else "не создан"
    notes_count = await db.door_note_count(user_id)

    text = (
        "🏡 <b>Моя комната</b>\n\n"
        f"🔖 Ник комнаты: {escape(nickname)}\n\n"
        "🌧 За окном: тихий дождь\n"
        f"🕯 Свет: {escape(room_light(stats))}\n"
        f"📚 Полка: {escape(room_shelf(stats))}\n"
        f"🦊 Рядом: {escape(nearby_pet_name(pets_rows))}\n\n"
        f"Страниц: {stats['book']}\n"
        f"Моментов: {stats['moments']}\n"
        f"Писем: {stats['letters']}\n"
        f"Ответов дня: {stats['answers']}\n"
        f"Питомцев: {stats['pets']}\n"
        f"Записок у двери: {notes_count}\n\n"
        f"{escape(room_atmosphere(stats))}"
    )
    await message.answer(text, reply_markup=room_menu(bool(profile and profile["room_nickname"])))
    await notify_room_updates(message, db, user_id)


@router.message(StateFilter(None), F.text == MENU_MIRROR)
async def mirror_start(message: Message, state: FSMContext, db: Database) -> None:
    await get_user_id(message, db)
    await state.set_state(MirrorForm.waiting_text)
    await message.answer(
        "<b>🪞 Зеркало</b>\n\n"
        "Что ты сейчас чувствуешь на самом деле?",
        reply_markup=back_menu(),
    )


@router.message(MirrorForm.waiting_text, F.text)
async def mirror_finish(message: Message, state: FSMContext, db: Database) -> None:
    text = clean_text(message)
    if text is None or is_navigation_text(text):
        await message.answer("Можно одной честной строкой.", reply_markup=back_menu())
        return

    user_id = await get_user_id(message, db)
    await db.add_mirror_entry(user_id, text)
    await state.clear()
    await message.answer(
        "🪞 Сохранено.\n\n"
        "Иногда зеркало просто держит свет.",
        reply_markup=main_menu(),
    )
    await after_important_action(message, db, user_id)


@router.message(StateFilter(None), F.text == MENU_SETTINGS)
async def settings(message: Message, db: Database) -> None:
    user_id = await get_user_id(message, db)
    profile = await db.room_profile(user_id)
    nickname = f"@{profile['room_nickname']}" if profile and profile["room_nickname"] else "не создан"
    privacy = PRIVACY_LABELS.get(str(profile["room_privacy"] if profile else "private"), PRIVACY_BY_NICKNAME)
    await message.answer(
        "<b>⚙️ Настройки</b>\n\n"
        "Lonelyroom хранит только то, что вы сами оставляете здесь.\n\n"
        f"🔖 Ник комнаты: {escape(nickname)}\n"
        f"🔒 Приватность: {escape(privacy)}",
        reply_markup=settings_menu(),
    )


@router.message(StateFilter(None), F.text == ROOM_CREATE_NICKNAME)
async def nickname_start(message: Message, state: FSMContext, db: Database) -> None:
    await get_user_id(message, db)
    await state.set_state(RoomNicknameForm.waiting_nickname)
    await message.answer(
        "<b>🔖 Ник комнаты</b>\n\n"
        "Придумайте ник комнаты.\n"
        "Например: lonely_mila\n\n"
        "Можно латинские буквы, цифры и _\n"
        "От 3 до 20 символов.",
        reply_markup=back_menu(),
    )


@router.message(RoomNicknameForm.waiting_nickname, F.text)
async def nickname_finish(message: Message, state: FSMContext, db: Database) -> None:
    text = clean_text(message)
    if text is None:
        await message.answer("Ник лучше написать одной строкой.", reply_markup=back_menu())
        return

    nickname = normalize_room_nickname(text)
    if not is_valid_room_nickname(nickname):
        await message.answer(
            "Эта дверь не запомнит такой ник.\n\n"
            "Нужны латинские буквы, цифры или _\n"
            "От 3 до 20 символов, без пробелов.",
            reply_markup=back_menu(),
        )
        return

    user_id = await get_user_id(message, db)
    if not await db.set_room_nickname(user_id, nickname):
        await message.answer(
            "Такой ник уже занял чью-то дверь.\n"
            "Попробуйте другой.",
            reply_markup=back_menu(),
        )
        return

    await state.clear()
    await message.answer(
        f"🔖 Ник комнаты создан: @{escape(nickname)}\n\n"
        "Теперь эту дверь можно найти по нику.",
        reply_markup=main_menu(),
    )


@router.message(StateFilter(None), F.text == ROOM_PRIVACY)
async def privacy_start(message: Message, db: Database) -> None:
    user_id = await get_user_id(message, db)
    profile = await db.room_profile(user_id)
    current = PRIVACY_LABELS.get(str(profile["room_privacy"] if profile else "private"), PRIVACY_BY_NICKNAME)
    await message.answer(
        "<b>🔒 Приватность комнаты</b>\n\n"
        f"Сейчас: {escape(current)}\n\n"
        "Пока комнату можно найти по нику, если ник создан.\n"
        "Личные записи гостям не показываются.",
        reply_markup=privacy_menu(),
    )


@router.message(StateFilter(None), F.text.in_(PRIVACY_OPTIONS))
async def privacy_save(message: Message, db: Database) -> None:
    text = clean_text(message)
    if text is None:
        await message.answer("Выберите один вариант.", reply_markup=privacy_menu())
        return

    user_id = await get_user_id(message, db)
    privacy = PRIVACY_VALUES[text]
    await db.set_room_privacy(user_id, privacy)
    await message.answer(
        f"🔒 Приватность сохранена: {escape(text)}",
        reply_markup=settings_menu(),
    )


@router.message(StateFilter(None), F.text == MENU_DOOR_NOTES)
async def door_notes(message: Message, db: Database) -> None:
    user_id = await get_user_id(message, db)
    rows = await db.latest_room_notes(user_id, limit=5)

    if not rows:
        await message.answer(
            "<b>💌 Записки у двери</b>\n\n"
            "У двери тихо.",
            reply_markup=main_menu(),
        )
        return

    items = []
    for index, row in enumerate(rows, start=1):
        author = f"@{row['guest_room_nickname']}" if row["guest_room_nickname"] else "от гостя без имени"
        items.append(
            f"{index}. “{escape(trim_text(str(row['text']), 180))}”\n"
            f"От: {escape(author)}"
        )

    await db.mark_room_notes_read(user_id)
    await message.answer(
        "<b>💌 Записки у двери</b>\n\n" + "\n\n".join(items),
        reply_markup=main_menu(),
    )


@router.message(StateFilter(None), F.text == MENU_ARCHIVE)
async def archive(message: Message, db: Database) -> None:
    user_id = await get_user_id(message, db)
    book_entries = await db.latest_book_entries(user_id, limit=5)
    moments = await db.latest_moments(user_id, limit=5)
    letters = await db.latest_letters(user_id, limit=5)
    answers = await db.latest_daily_answers(user_id, limit=5)

    letter_rows = []
    for row in letters:
        title = trim_text(str(row["title"]), 50)
        body = trim_text(str(row["body"]), 95)
        letter_rows.append({"text": f"{title}: {body}"})

    text = (
        "<b>🧳 Архив</b>\n\n"
        "Последние следы, оставленные в комнате.\n\n"
        f"{archive_block('📖 Страницы', book_entries)}\n\n"
        f"{archive_block('🕯 Моменты', moments)}\n\n"
        f"{archive_block('💌 Письма', letter_rows)}\n\n"
        f"{daily_answers_block(answers)}"
    )
    await message.answer(text, reply_markup=main_menu())


@router.message(StateFilter(None), F.text == MENU_BOOK)
async def book(message: Message, db: Database) -> None:
    await get_user_id(message, db)
    await message.answer(
        "<b>📖 Книга обо мне</b>\n\nЗдесь можно оставить маленькую страницу.",
        reply_markup=book_menu(),
    )


@router.message(StateFilter(None), F.text == BOOK_ADD)
async def add_book_entry_start(message: Message, state: FSMContext, db: Database) -> None:
    await get_user_id(message, db)
    await state.set_state(BookForm.waiting_text)
    await message.answer(
        "Напишите страницу.\nЧто о себе хочется запомнить?",
        reply_markup=back_menu(),
    )


@router.message(StateFilter(None), F.text == BOOK_READ)
async def read_book_entries(message: Message, db: Database) -> None:
    user_id = await get_user_id(message, db)
    rows = await db.latest_book_entries(user_id)
    await message.answer(
        f"<b>📚 Последние страницы</b>\n\n{format_short_list(rows)}",
        reply_markup=book_menu(),
    )


@router.message(BookForm.waiting_text, F.text)
async def add_book_entry_finish(message: Message, state: FSMContext, db: Database) -> None:
    text = clean_text(message)
    if text is None or is_navigation_text(text):
        await message.answer("Лучше одной простой строкой.", reply_markup=back_menu())
        return

    user_id = await get_user_id(message, db)
    await db.add_book_entry(user_id, text)
    await state.clear()
    await message.answer(
        "📖 Страница сохранена.\n\nОна легла в книгу, как тихая закладка.",
        reply_markup=book_menu(),
    )
    await after_important_action(message, db, user_id)


@router.message(StateFilter(None), F.text == MENU_DAILY)
async def daily_question(message: Message, state: FSMContext, db: Database) -> None:
    user_id = await get_user_id(message, db)
    today = date.today()
    answer_date = today.isoformat()
    question = question_for_day(today)
    saved = await db.get_daily_answer(user_id, answer_date)

    if saved is not None:
        text = (
            "<b>🌙 Вопрос дня</b>\n\n"
            f"{escape(str(saved['question']))}\n\n"
            f"Ваш ответ:\n{escape(trim_text(str(saved['answer']), 220))}"
        )
        await message.answer(text, reply_markup=main_menu())
        return

    await state.update_data(question=question, answer_date=answer_date)
    await state.set_state(DailyQuestionForm.waiting_answer)
    await message.answer(
        f"<b>🌙 Вопрос дня</b>\n\n{escape(question)}",
        reply_markup=back_menu(),
    )


@router.message(DailyQuestionForm.waiting_answer, F.text)
async def daily_question_finish(message: Message, state: FSMContext, db: Database) -> None:
    text = clean_text(message)
    if text is None or is_navigation_text(text):
        await message.answer("Можно ответить одной фразой.", reply_markup=back_menu())
        return

    data = await state.get_data()
    question = str(data["question"])
    answer_date = str(data["answer_date"])
    user_id = await get_user_id(message, db)
    await db.save_daily_answer(user_id, answer_date, question, text)
    await state.clear()
    await message.answer("🌙 Ответ сохранён.\n\nПусть немного побудет здесь, в тишине.", reply_markup=main_menu())
    await after_important_action(message, db, user_id)


@router.message(StateFilter(None), F.text == MENU_MOOD)
async def mood_start(message: Message, db: Database) -> None:
    await get_user_id(message, db)
    await message.answer(
        "<b>🌧 Настроение дня</b>\n\n"
        "Какой сегодня воздух внутри комнаты?",
        reply_markup=mood_menu(),
    )


@router.message(StateFilter(None), F.text.in_(MOODS))
async def mood_save(message: Message, db: Database) -> None:
    text = clean_text(message)
    if text is None:
        await message.answer("Выберите настроение одним словом.", reply_markup=mood_menu())
        return

    user_id = await get_user_id(message, db)
    await db.save_mood(user_id, date.today().isoformat(), text)
    await message.answer(
        f"🌧 Настроение сохранено: {escape(text)}.\n\n"
        "Пусть день останется таким, каким он был на самом деле.",
        reply_markup=main_menu(),
    )
    await after_important_action(message, db, user_id)


@router.message(StateFilter(None), F.text == OLD_MENU_MOMENT)
@router.message(StateFilter(None), F.text == MENU_MOMENT)
async def moment_start(message: Message, state: FSMContext, db: Database) -> None:
    await get_user_id(message, db)
    await state.set_state(MomentForm.waiting_text)
    await message.answer(
        "<b>🕯 Моменты</b>\n\n"
        "Какое маленькое воспоминание оставить здесь?\n"
        "Можно одной строкой, как заметку на полях книги.",
        reply_markup=back_menu(),
    )


@router.message(MomentForm.waiting_text, F.text)
async def moment_finish(message: Message, state: FSMContext, db: Database) -> None:
    text = clean_text(message)
    if text is None or is_navigation_text(text):
        await message.answer("Оставьте сам момент.\nКак он звучит в памяти?", reply_markup=back_menu())
        return

    user_id = await get_user_id(message, db)
    await db.add_moment(user_id, text)
    await state.clear()
    await message.answer(
        "🕯 Момент сохранён.\n\n"
        "Когда-нибудь ты вернёшься сюда и вспомнишь этот день.",
        reply_markup=main_menu(),
    )
    await after_important_action(message, db, user_id)


@router.message(StateFilter(None), F.text == MENU_LETTERS)
async def letter_self_start(message: Message, state: FSMContext, db: Database) -> None:
    await get_user_id(message, db)
    await state.update_data(title="Письмо себе", letter_mode="simple")
    await state.set_state(LetterForm.waiting_body)
    await message.answer(
        "<b>💌 Письмо себе</b>\n\n"
        "Напишите то, что хочется сохранить для себя будущего.\n"
        "Пусть это будет тихо и честно.",
        reply_markup=back_menu(),
    )


@router.message(StateFilter(None), F.text == OLD_MENU_LETTERS)
async def letters(message: Message, db: Database) -> None:
    await get_user_id(message, db)
    await message.answer(
        "<b>💌 Письма</b>\n\n"
        "Здесь хранятся слова, которые можно открыть позже, как конверт из прошлого.",
        reply_markup=letters_menu(),
    )


@router.message(StateFilter(None), F.text == LETTER_WRITE)
async def letter_title_start(message: Message, state: FSMContext, db: Database) -> None:
    await get_user_id(message, db)
    await state.set_state(LetterForm.waiting_title)
    await message.answer("Тема письма?", reply_markup=back_menu())


@router.message(LetterForm.waiting_title, F.text)
async def letter_body_start(message: Message, state: FSMContext) -> None:
    text = clean_text(message)
    if text is None or is_navigation_text(text):
        await message.answer("Напишите короткую тему.", reply_markup=back_menu())
        return

    await state.update_data(title=trim_text(text, 80), letter_mode="detailed")
    await state.set_state(LetterForm.waiting_body)
    await message.answer("Теперь само письмо.\nКак бы вы сказали это себе тихо?", reply_markup=back_menu())


@router.message(LetterForm.waiting_body, F.text)
async def letter_finish(message: Message, state: FSMContext, db: Database) -> None:
    text = clean_text(message)
    if text is None or is_navigation_text(text):
        await message.answer("Напишите само письмо.\nПусть это будет несколько ваших строк.", reply_markup=back_menu())
        return

    data = await state.get_data()
    title = str(data.get("title", "Письмо себе"))
    letter_mode = str(data.get("letter_mode", "detailed"))
    user_id = await get_user_id(message, db)
    await db.add_letter(user_id, title, text)
    await state.clear()
    await message.answer(
        "💌 Письмо сохранено.\n\n"
        "Иногда полезно услышать собственный голос спустя время.",
        reply_markup=main_menu() if letter_mode == "simple" else letters_menu(),
    )
    await after_important_action(message, db, user_id)


@router.message(StateFilter(None), F.text == LETTER_READ)
async def read_letters(message: Message, db: Database) -> None:
    user_id = await get_user_id(message, db)
    rows = await db.latest_letters(user_id)

    if not rows:
        await message.answer(f"<b>📬 Последние письма</b>\n\n{EMPTY_TEXT}", reply_markup=letters_menu())
        return

    items = []
    for index, row in enumerate(rows, start=1):
        title = escape(trim_text(str(row["title"]), 80))
        body = escape(trim_text(str(row["body"]), 140))
        items.append(f"{index}. <b>{title}</b>\n{body}")

    await message.answer(
        f"<b>📬 Последние письма</b>\n\n" + "\n\n".join(items),
        reply_markup=letters_menu(),
    )


@router.message(StateFilter(None), F.text == MENU_EVENING)
async def evening(message: Message, db: Database) -> None:
    await get_user_id(message, db)
    recipe = choice(EVENING_RECIPES)
    text = (
        "<b>☕ Вечер на сегодня</b>\n\n"
        f"Напиток: {escape(recipe.drink)}\n"
        f"Звук: {escape(recipe.sound)}\n"
        f"Дело: {escape(recipe.action)}\n"
        f"Вопрос: {escape(recipe.question)}\n\n"
        "Без спешки."
    )
    await message.answer(text, reply_markup=main_menu())


@router.message(StateFilter(None), F.text == MENU_FRIEND_ROOMS)
async def friend_rooms_start(message: Message, state: FSMContext, db: Database) -> None:
    await get_user_id(message, db)
    await state.set_state(FriendRoomForm.waiting_nickname)
    await message.answer(
        "<b>🚪 Комнаты друзей</b>\n\n"
        "Введите ник комнаты друга.\n"
        "Например: lonely_mila",
        reply_markup=back_menu(),
    )


@router.message(FriendRoomForm.waiting_nickname, F.text)
async def friend_room_find(message: Message, state: FSMContext, db: Database) -> None:
    text = clean_text(message)
    if text is None:
        await message.answer("Ник комнаты лучше написать одной строкой.", reply_markup=back_menu())
        return

    nickname = normalize_room_nickname(text)
    if not is_valid_room_nickname(nickname):
        await message.answer(
            "Такая дверь не находится.\n"
            "Попробуйте ник без пробелов.",
            reply_markup=back_menu(),
        )
        return

    profile = await db.find_room_by_nickname(nickname)
    if profile is None:
        await message.answer(
            "Дверь не найдена.\n\n"
            "Может быть, ник написан иначе.",
            reply_markup=back_menu(),
        )
        return

    await state.update_data(room_owner_id=int(profile["user_id"]), room_nickname=nickname)
    await state.set_state(FriendRoomForm.viewing_room)
    await message.answer(
        await guest_room_text(db, int(profile["user_id"]), nickname),
        reply_markup=guest_room_menu(),
    )


@router.message(FriendRoomForm.viewing_room, F.text == GUEST_LEAVE_NOTE)
async def guest_note_start(message: Message, state: FSMContext) -> None:
    data = await state.get_data()
    await state.set_state(RoomNoteForm.waiting_text)
    await state.update_data(**data)
    await message.answer(
        "Что оставить у двери этой комнаты?",
        reply_markup=back_menu(),
    )


@router.message(RoomNoteForm.waiting_text, F.text)
async def guest_note_finish(message: Message, state: FSMContext, db: Database) -> None:
    text = clean_text(message)
    if text is None or is_navigation_text(text):
        await message.answer("Записка может быть совсем короткой.", reply_markup=back_menu())
        return

    data = await state.get_data()
    room_owner_id = int(data["room_owner_id"])
    guest_user_id = await get_user_id(message, db)
    guest_profile = await db.room_profile(guest_user_id)
    guest_nickname = str(guest_profile["room_nickname"]) if guest_profile and guest_profile["room_nickname"] else None

    await db.add_room_note(room_owner_id, guest_user_id, guest_nickname, text)
    await state.clear()
    await message.answer(
        "💌 Записка оставлена у двери.\n\n"
        "Она осталась ждать хозяина.",
        reply_markup=main_menu(),
    )


@router.message(FriendRoomForm.viewing_room, F.text == GUEST_LEAVE_LIGHT)
async def guest_light(message: Message, state: FSMContext, db: Database) -> None:
    data = await state.get_data()
    room_owner_id = int(data["room_owner_id"])
    guest_user_id = await get_user_id(message, db)
    await db.add_room_light(room_owner_id, guest_user_id)
    await message.answer(
        "✨ Огонёк оставлен у двери.\n\n"
        "Он будет тихо светить здесь.",
        reply_markup=guest_room_menu(),
    )


@router.message(StateFilter(None), F.text == MENU_PETS)
async def pets(message: Message, db: Database) -> None:
    user_id = await get_user_id(message, db)
    await db.unlock_eligible_pets(user_id)
    pets_rows = await db.latest_pets(user_id)
    unlocked_codes = {str(row["pet_code"]) for row in pets_rows}

    if not pets_rows:
        closed_items = []
        for pet in PETS:
            closed_items.append(f"{pet.name}\nОткроется: {pet.condition_text}")

        text = (
            "🦊 Здесь пока тихо.\n\n"
            "Но кажется, кто-то уже прислушивается к твоей комнате.\n\n"
            "<b>Закрытые питомцы</b>\n\n"
            + "\n\n".join(escape(item) for item in closed_items)
        )
        await message.answer(text, reply_markup=main_menu())
        return

    opened_items = []
    closed_items = []

    for pet in PETS:
        if pet.code in unlocked_codes:
            opened_items.append(f"<b>{escape(pet.name)}</b>\n{escape(pet.description)}")
        else:
            closed_items.append(f"{escape(pet.name)}\nОткроется: {escape(pet.condition_text)}")

    opened_block = "<b>Открытые питомцы</b>\n\n" + "\n\n".join(opened_items)
    closed_block = ""
    if closed_items:
        closed_block = "\n\n<b>Закрытые питомцы</b>\n\n" + "\n\n".join(closed_items)

    await message.answer(
        "🦊 <b>Питомцы</b>\n\n"
        f"{opened_block}"
        f"{closed_block}",
        reply_markup=main_menu(),
    )


@router.message(StateFilter(None), F.text == MENU_MEDIA)
async def media(message: Message, db: Database) -> None:
    await get_user_id(message, db)
    await message.answer(
        "<b>🎬 Медиа</b>\n\n"
        "Полка для вечеров, когда хочется не шума, а настроения.\n"
        "Выберите, что поставить рядом с комнатой.",
        reply_markup=media_menu(),
    )


@router.message(StateFilter(None), F.text == MEDIA_BOOKS)
async def media_books(message: Message, db: Database) -> None:
    await get_user_id(message, db)
    await message.answer(
        "<b>📚 Книги</b>\n\n"
        "Скоро здесь появится тихая полка с книгами для дождливых вечеров.",
        reply_markup=media_menu(),
    )


@router.message(StateFilter(None), F.text == MEDIA_MOVIES)
async def media_movies(message: Message, db: Database) -> None:
    await get_user_id(message, db)
    await message.answer(
        "<b>🎬 Фильмы</b>\n\n"
        "Скоро здесь будет маленький кинозал: плед, приглушённый свет и пауза от дня.",
        reply_markup=media_menu(),
    )


@router.message(StateFilter(None), F.text == MEDIA_MUSIC)
async def media_music(message: Message, db: Database) -> None:
    await get_user_id(message, db)
    await message.answer(
        "<b>🎵 Музыка</b>\n\n"
        "Скоро здесь будут плейлисты, которые звучат как вечернее окно после дождя.",
        reply_markup=media_menu(),
    )


@router.message(StateFilter(None), F.text == MENU_TALK)
async def talk_start(message: Message, state: FSMContext, db: Database) -> None:
    await get_user_id(message, db)
    await state.set_state(TalkForm.waiting_text)
    await message.answer(
        "Я здесь.\nЧто сейчас внутри?",
        reply_markup=back_menu(),
    )


@router.message(TalkForm.waiting_text, F.text)
async def talk_finish(message: Message, state: FSMContext, db: Database) -> None:
    text = clean_text(message)
    if text is None or is_navigation_text(text):
        await message.answer("Можно одной строкой.", reply_markup=back_menu())
        return

    user_id = await get_user_id(message, db)
    await answer_conversation(message, db, user_id, text, in_talk_mode=True)


@router.message(StateFilter(None))
async def fallback(message: Message, db: Database) -> None:
    text = clean_text(message)
    user_id = await get_user_id(message, db)

    if text is None:
        await message.answer("Лучше текстом.\nЯ так смогу понять точнее.", reply_markup=main_menu())
        return

    await answer_conversation(message, db, user_id, text, in_talk_mode=False)


@router.message()
async def state_fallback(message: Message) -> None:
    await message.answer("Лучше отправить текстом.\nИли вернуться в меню.", reply_markup=back_menu())

from datetime import date
from html import escape
from random import choice

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
    LETTER_READ,
    LETTER_WRITE,
    MENU_BOOK,
    MENU_DAILY,
    MENU_EVENING,
    MENU_LETTERS,
    MENU_MOMENT,
    MENU_ROOM,
    MENU_TALK,
    back_menu,
    book_menu,
    letters_menu,
    main_menu,
)
from lonelyroom_bot.states import BookForm, DailyQuestionForm, LetterForm, MomentForm, TalkForm
from lonelyroom_bot.texts import (
    EMPTY_TEXT,
    EVENING_RECIPES,
    MENU_TEXT,
    WELCOME_TEXT,
    question_for_day,
    trim_text,
)


router = Router(name="lonelyroom")

NAVIGATION_TEXTS = {
    MENU_ROOM,
    MENU_BOOK,
    MENU_DAILY,
    MENU_MOMENT,
    MENU_LETTERS,
    MENU_EVENING,
    MENU_TALK,
    BOOK_ADD,
    BOOK_READ,
    LETTER_WRITE,
    LETTER_READ,
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


@router.message(CommandStart())
async def start(message: Message, state: FSMContext, db: Database) -> None:
    await state.clear()
    await get_user_id(message, db)
    await message.answer(WELCOME_TEXT, reply_markup=main_menu())


@router.message(Command("menu"))
async def menu(message: Message, state: FSMContext, db: Database) -> None:
    await state.clear()
    await get_user_id(message, db)
    await message.answer(MENU_TEXT, reply_markup=main_menu())


@router.message(F.text == BACK)
async def back_to_menu(message: Message, state: FSMContext, db: Database) -> None:
    await state.clear()
    await get_user_id(message, db)
    await message.answer(MENU_TEXT, reply_markup=main_menu())


@router.message(StateFilter(None), F.text == MENU_ROOM)
async def show_room(message: Message, db: Database) -> None:
    user_id = await get_user_id(message, db)
    stats = await db.room_stats(user_id)
    moments = await db.latest_moments(user_id, limit=1)
    last_moment = ""

    if moments:
        last_moment = f"\n\nПоследний момент:\n{escape(trim_text(str(moments[0]['text']), 120))}"

    text = (
        "<b>🏡 Моя комната</b>\n\n"
        f"Страниц: {stats['book']}\n"
        f"Моментов: {stats['moments']}\n"
        f"Писем: {stats['letters']}\n"
        f"Ответов дня: {stats['answers']}\n"
        f"Сообщений в разговоре: {stats['conversation']}"
        f"{last_moment}\n\n"
        "каждый человек — это целая комната."
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
        "Страница сохранена.\nОна теперь в книге.",
        reply_markup=book_menu(),
    )


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
    await message.answer("Ответ сохранен.\nПусть он побудет здесь.", reply_markup=main_menu())


@router.message(StateFilter(None), F.text == MENU_MOMENT)
async def moment_start(message: Message, state: FSMContext, db: Database) -> None:
    await get_user_id(message, db)
    await state.set_state(MomentForm.waiting_text)
    await message.answer(
        "Какой момент сохранить?\nЧто было живым сегодня?",
        reply_markup=back_menu(),
    )


@router.message(MomentForm.waiting_text, F.text)
async def moment_finish(message: Message, state: FSMContext, db: Database) -> None:
    text = clean_text(message)
    if text is None or is_navigation_text(text):
        await message.answer("Напишите сам момент.", reply_markup=back_menu())
        return

    user_id = await get_user_id(message, db)
    await db.add_moment(user_id, text)
    await state.clear()
    await message.answer("Момент сохранен.\nТихо и бережно.", reply_markup=main_menu())


@router.message(StateFilter(None), F.text == MENU_LETTERS)
async def letters(message: Message, db: Database) -> None:
    await get_user_id(message, db)
    await message.answer(
        "<b>💌 Письма</b>\n\nМожно оставить себе пару честных строк.",
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

    await state.update_data(title=trim_text(text, 80))
    await state.set_state(LetterForm.waiting_body)
    await message.answer("Теперь само письмо.\nКак бы вы сказали это себе тихо?", reply_markup=back_menu())


@router.message(LetterForm.waiting_body, F.text)
async def letter_finish(message: Message, state: FSMContext, db: Database) -> None:
    text = clean_text(message)
    if text is None or is_navigation_text(text):
        await message.answer("Напишите текст письма.", reply_markup=back_menu())
        return

    data = await state.get_data()
    title = str(data["title"])
    user_id = await get_user_id(message, db)
    await db.add_letter(user_id, title, text)
    await state.clear()
    await message.answer("Письмо сохранено.\nОно будет ждать вас.", reply_markup=letters_menu())


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

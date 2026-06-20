from aiogram.fsm.state import State, StatesGroup


class BookForm(StatesGroup):
    waiting_text = State()


class DailyQuestionForm(StatesGroup):
    waiting_answer = State()


class MomentForm(StatesGroup):
    waiting_text = State()


class LetterForm(StatesGroup):
    waiting_title = State()
    waiting_body = State()


class TalkForm(StatesGroup):
    waiting_text = State()

from dataclasses import dataclass
from datetime import date


WELCOME_TEXT = (
    "🌙 Lonelyroom открыт.\n\n"
    "Здесь не нужно спешить.\n\n"
    "Каждый человек — это целая комната.\n"
    "Некоторые двери мы открываем впервые.\n"
    "Некоторые воспоминания ждут нас годами.\n\n"
    "Выберите уголок, куда хочется зайти."
)

MENU_TEXT = "Выберите уголок, куда хочется зайти."

EMPTY_TEXT = "Здесь пока тихо, как в комнате перед дождём."

SMALL_DISCOVERIES = [
    "В комнате стало немного теплее.",
    "На полке появился новый след этого дня.",
    "Кажется, здесь кто-то тихо устроился рядом.",
]

DAILY_QUESTIONS = [
    "Что сегодня хочется беречь в себе?",
    "Какая маленькая вещь сделала день мягче?",
    "Где внутри стало чуть легче?",
    "Что можно отпустить хотя бы на вечер?",
    "Какая мысль сегодня чаще возвращалась?",
    "За что себе можно сказать спасибо?",
    "Что сегодня было настоящим?",
]


@dataclass(frozen=True)
class EveningRecipe:
    drink: str
    sound: str
    action: str
    question: str


EVENING_RECIPES = [
    EveningRecipe(
        drink="чай с лимоном",
        sound="тихий плейлист без слов",
        action="убрать одну маленькую поверхность",
        question="что сегодня можно не додумывать?",
    ),
    EveningRecipe(
        drink="какао или теплое молоко",
        sound="дождь на фоне",
        action="зажечь свечу на десять минут",
        question="где сейчас хочется мягкости?",
    ),
    EveningRecipe(
        drink="мята или ромашка",
        sound="старый спокойный альбом",
        action="записать три простые вещи дня",
        question="что уже достаточно?",
    ),
    EveningRecipe(
        drink="вода в любимой кружке",
        sound="тишина комнаты",
        action="положить телефон экраном вниз",
        question="какой темп мне подходит сегодня?",
    ),
]


def question_for_day(day: date) -> str:
    index = day.toordinal() % len(DAILY_QUESTIONS)
    return DAILY_QUESTIONS[index]


def trim_text(value: str, limit: int = 160) -> str:
    text = " ".join(value.split())
    if len(text) <= limit:
        return text
    return f"{text[: limit - 1].rstrip()}…"

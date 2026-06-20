from collections.abc import Sequence
from dataclasses import dataclass
from html import escape
from string import punctuation

from aiosqlite import Row

from lonelyroom_bot.texts import trim_text


@dataclass(frozen=True)
class ConversationReply:
    text: str


def build_conversation_reply(user_text: str, history: Sequence[Row]) -> ConversationReply:
    text = " ".join(user_text.split())
    normalized = normalize(text)
    previous_user_text = last_user_message(history)

    if not text:
        return ConversationReply("я рядом.\nчто хочется сказать?")

    if contains_any(normalized, ("привет", "здравствуй", "добрый", "хай")):
        if previous_user_text:
            return ConversationReply(
                f"привет. я помню, до этого было: «{quote(previous_user_text)}».\nкак ты сейчас?"
            )
        return ConversationReply("привет.\nкак ты сейчас?")

    if is_tiny_sigh(normalized):
        return ConversationReply(memory_bridge(previous_user_text, "что случилось?"))

    if contains_any(normalized, ("груст", "печаль", "тоск", "плак")):
        return ConversationReply("расскажешь, что произошло?")

    if contains_any(normalized, ("устал", "уста", "вымот", "нет сил", "выгор")):
        return ConversationReply("давно так себя чувствуешь?")

    if contains_any(normalized, ("тревож", "страш", "паник", "боюсь", "нерв")):
        return ConversationReply("похоже, внутри много тревоги.\nона про что-то конкретное?")

    if contains_any(normalized, ("одинок", "одна", "один", "никому", "пусто")):
        return ConversationReply("одиночество сегодня прям рядом.\nэто больше про людей или про ощущение внутри?")

    if contains_any(normalized, ("злюсь", "бесит", "ненавиж", "раздраж", "обид")):
        return ConversationReply("звучит, будто тебя задели.\nчто именно сильнее всего?")

    if contains_any(normalized, ("не знаю", "хз", "не понимаю", "не могу понять")):
        return ConversationReply(memory_bridge(previous_user_text, "можно не знать сразу.\nс чего это началось?"))

    if contains_any(normalized, ("хорошо", "рад", "рада", "счаст", "тепло", "получилось")):
        return ConversationReply("мне приятно это слышать.\nчто именно сделало день теплее?")

    if contains_any(normalized, ("опять", "снова", "как вчера", "как тогда")) and previous_user_text:
        return ConversationReply(
            f"похоже, это возвращается к тому, что уже было: «{quote(previous_user_text)}».\nчто сейчас изменилось?"
        )

    if looks_like_story(text):
        return ConversationReply(continue_story(text))

    if previous_user_text:
        return ConversationReply(
            f"я помню, до этого было: «{quote(previous_user_text)}».\nэто связано с тем, что сейчас написано?"
        )

    return ConversationReply("я читаю тебя.\nчто в этом для тебя самое важное?")


def normalize(text: str) -> str:
    lowered = text.lower().replace("ё", "е")
    return lowered.strip(f"{punctuation}—…«»“”„ ")


def is_tiny_sigh(text: str) -> bool:
    sighs = {
        "",
        "эх",
        "ех",
        "мм",
        "м",
        "мда",
        "да уж",
        "блин",
        "капец",
        "ладно",
        "...",
    }
    return text in sighs or len(text) <= 3


def contains_any(text: str, needles: Sequence[str]) -> bool:
    return any(needle in text for needle in needles)


def last_user_message(history: Sequence[Row]) -> str | None:
    for row in reversed(history):
        if row["role"] == "user":
            return str(row["text"])
    return None


def memory_bridge(previous_user_text: str | None, fallback: str) -> str:
    if previous_user_text is None:
        return fallback

    return f"это про то, что было раньше: «{quote(previous_user_text)}»?\n{fallback}"


def looks_like_story(text: str) -> bool:
    return len(text) > 70 or any(mark in text for mark in (",", " потому ", " когда ", " и "))


def continue_story(text: str) -> str:
    fragment = quote(text)
    if contains_any(normalize(text), ("работ", "учеб", "дел", "задач")):
        return f"похоже, «{fragment}» правда вымотало.\nчто было самым тяжелым?"

    if contains_any(normalize(text), ("мама", "папа", "друг", "подруга", "парень", "девушка", "люди")):
        return f"в этом слышно много про отношения.\nчто тебя задело сильнее всего?"

    return f"мне откликнулось вот это: «{fragment}».\nчто в этом болит больше всего?"


def quote(text: str, limit: int = 56) -> str:
    return escape(trim_text(text, limit))

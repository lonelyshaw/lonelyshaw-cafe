from dataclasses import dataclass
from typing import Callable


Stats = dict[str, int]


@dataclass(frozen=True)
class Pet:
    code: str
    emoji: str
    title: str
    description: str
    condition_text: str
    is_ready: Callable[[Stats], bool]
    arrival_text: str

    @property
    def name(self) -> str:
        return f"{self.emoji} {self.title}"


PETS = (
    Pet(
        code="forest_fox",
        emoji="🦊",
        title="Лесной лисёнок",
        description="Он появляется рядом с теми, кто учится быть мягче к себе.",
        condition_text="1 ответ на вопрос дня + 1 страница в книге + 1 сохранённый момент",
        is_ready=lambda stats: stats["answers"] >= 1 and stats["book"] >= 1 and stats["moments"] >= 1,
        arrival_text="Лесной лисёнок тихо устроился рядом.",
    ),
    Pet(
        code="night_owl",
        emoji="🦉",
        title="Ночная сова",
        description="Она прилетает к тем, кто часто возвращается к своим мыслям вечером.",
        condition_text="5 ответов дня",
        is_ready=lambda stats: stats["answers"] >= 5,
        arrival_text="Ночная сова бесшумно опустилась на полку.",
    ),
    Pet(
        code="cafe_cat",
        emoji="🐈",
        title="Кафейный кот",
        description="Он любит тёплый свет, книги и тихие разговоры.",
        condition_text="3 сохранённых момента",
        is_ready=lambda stats: stats["moments"] >= 3,
        arrival_text="Кафейный кот свернулся у тёплого света.",
    ),
    Pet(
        code="rain_rabbit",
        emoji="🐇",
        title="Дождевой кролик",
        description="Он появляется в комнатах, где умеют замечать маленькие радости.",
        condition_text="3 страницы в книге обо мне",
        is_ready=lambda stats: stats["book"] >= 3,
        arrival_text="Дождевой кролик тихо выглянул из-под пледа.",
    ),
    Pet(
        code="mist_deer",
        emoji="🦌",
        title="Олень туманных холмов",
        description="Он приходит к тем, кто долго идёт к себе, но не сдаётся.",
        condition_text="10 любых действий в комнате",
        is_ready=lambda stats: action_total(stats) >= 10,
        arrival_text="Олень туманных холмов остановился у самой двери.",
    ),
)

PET_BY_CODE = {pet.code: pet for pet in PETS}
FIRST_PET = PETS[0]


def action_total(stats: Stats) -> int:
    return (
        stats["book"]
        + stats["moments"]
        + stats["letters"]
        + stats["answers"]
        + stats["moods"]
        + stats["mirror"]
    )


def eligible_pets(stats: Stats) -> list[Pet]:
    return [pet for pet in PETS if pet.is_ready(stats)]

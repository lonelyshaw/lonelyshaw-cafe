import os
from dataclasses import dataclass

from dotenv import load_dotenv


@dataclass(frozen=True)
class Config:
    bot_token: str
    database_path: str


def load_config() -> Config:
    load_dotenv()

    bot_token = os.getenv("BOT_TOKEN", "").strip()
    if not bot_token:
        raise RuntimeError("Укажите BOT_TOKEN в .env")

    database_path = os.getenv("DATABASE_PATH", "data/lonelyroom.sqlite3").strip()
    return Config(bot_token=bot_token, database_path=database_path)

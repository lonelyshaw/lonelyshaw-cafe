from pathlib import Path
from typing import Any

import aiosqlite


SCHEMA = """
PRAGMA foreign_keys = ON;

CREATE TABLE IF NOT EXISTS users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    telegram_id INTEGER NOT NULL UNIQUE,
    username TEXT,
    first_name TEXT,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    last_seen_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP
);

CREATE TABLE IF NOT EXISTS book_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    category TEXT NOT NULL DEFAULT 'about',
    text TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS daily_answers (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    answer_date TEXT NOT NULL,
    question TEXT NOT NULL,
    answer TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE (user_id, answer_date)
);

CREATE TABLE IF NOT EXISTS moments (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS letters (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    title TEXT NOT NULL,
    body TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS conversation_messages (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    role TEXT NOT NULL CHECK (role IN ('user', 'bot')),
    text TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE INDEX IF NOT EXISTS idx_book_entries_user_created
    ON book_entries (user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_daily_answers_user_date
    ON daily_answers (user_id, answer_date DESC);

CREATE INDEX IF NOT EXISTS idx_moments_user_created
    ON moments (user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_letters_user_created
    ON letters (user_id, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_conversation_messages_user_created
    ON conversation_messages (user_id, created_at DESC, id DESC);
"""


class Database:
    def __init__(self, path: str) -> None:
        self.path = Path(path)
        self.connection: aiosqlite.Connection | None = None

    async def connect(self) -> None:
        if self.path.parent != Path("."):
            self.path.parent.mkdir(parents=True, exist_ok=True)

        self.connection = await aiosqlite.connect(self.path)
        self.connection.row_factory = aiosqlite.Row
        await self.connection.executescript(SCHEMA)
        await self.connection.commit()

    async def close(self) -> None:
        if self.connection is not None:
            await self.connection.close()
            self.connection = None

    def _db(self) -> aiosqlite.Connection:
        if self.connection is None:
            raise RuntimeError("База данных не подключена")
        return self.connection

    async def ensure_user(
        self,
        telegram_id: int,
        username: str | None,
        first_name: str | None,
    ) -> int:
        db = self._db()
        await db.execute(
            """
            INSERT INTO users (telegram_id, username, first_name)
            VALUES (?, ?, ?)
            ON CONFLICT(telegram_id) DO UPDATE SET
                username = excluded.username,
                first_name = excluded.first_name,
                last_seen_at = CURRENT_TIMESTAMP
            """,
            (telegram_id, username, first_name),
        )
        await db.commit()

        async with db.execute(
            "SELECT id FROM users WHERE telegram_id = ?",
            (telegram_id,),
        ) as cursor:
            row = await cursor.fetchone()

        if row is None:
            raise RuntimeError("Не удалось найти пользователя")
        return int(row["id"])

    async def room_stats(self, user_id: int) -> dict[str, int]:
        db = self._db()
        tables = {
            "book": "book_entries",
            "moments": "moments",
            "letters": "letters",
            "answers": "daily_answers",
            "conversation": "conversation_messages",
        }
        stats: dict[str, int] = {}

        for key, table in tables.items():
            async with db.execute(
                f"SELECT COUNT(*) AS amount FROM {table} WHERE user_id = ?",
                (user_id,),
            ) as cursor:
                row = await cursor.fetchone()
                stats[key] = int(row["amount"] if row else 0)

        return stats

    async def add_book_entry(self, user_id: int, text: str) -> None:
        await self._execute_write(
            "INSERT INTO book_entries (user_id, text) VALUES (?, ?)",
            (user_id, text),
        )

    async def latest_book_entries(self, user_id: int, limit: int = 5) -> list[aiosqlite.Row]:
        return await self._fetch_latest(
            "SELECT text, created_at FROM book_entries WHERE user_id = ? ORDER BY created_at DESC, id DESC LIMIT ?",
            user_id,
            limit,
        )

    async def get_daily_answer(
        self,
        user_id: int,
        answer_date: str,
    ) -> aiosqlite.Row | None:
        db = self._db()
        async with db.execute(
            """
            SELECT question, answer, created_at
            FROM daily_answers
            WHERE user_id = ? AND answer_date = ?
            """,
            (user_id, answer_date),
        ) as cursor:
            return await cursor.fetchone()

    async def save_daily_answer(
        self,
        user_id: int,
        answer_date: str,
        question: str,
        answer: str,
    ) -> None:
        await self._execute_write(
            """
            INSERT INTO daily_answers (user_id, answer_date, question, answer)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(user_id, answer_date) DO UPDATE SET
                question = excluded.question,
                answer = excluded.answer,
                created_at = CURRENT_TIMESTAMP
            """,
            (user_id, answer_date, question, answer),
        )

    async def add_moment(self, user_id: int, text: str) -> None:
        await self._execute_write(
            "INSERT INTO moments (user_id, text) VALUES (?, ?)",
            (user_id, text),
        )

    async def latest_moments(self, user_id: int, limit: int = 5) -> list[aiosqlite.Row]:
        return await self._fetch_latest(
            "SELECT text, created_at FROM moments WHERE user_id = ? ORDER BY created_at DESC, id DESC LIMIT ?",
            user_id,
            limit,
        )

    async def add_letter(self, user_id: int, title: str, body: str) -> None:
        await self._execute_write(
            "INSERT INTO letters (user_id, title, body) VALUES (?, ?, ?)",
            (user_id, title, body),
        )

    async def latest_letters(self, user_id: int, limit: int = 5) -> list[aiosqlite.Row]:
        return await self._fetch_latest(
            "SELECT title, body, created_at FROM letters WHERE user_id = ? ORDER BY created_at DESC, id DESC LIMIT ?",
            user_id,
            limit,
        )

    async def add_conversation_message(self, user_id: int, role: str, text: str) -> None:
        if role not in {"user", "bot"}:
            raise ValueError("role должен быть 'user' или 'bot'")

        await self._execute_write(
            "INSERT INTO conversation_messages (user_id, role, text) VALUES (?, ?, ?)",
            (user_id, role, text),
        )

    async def latest_conversation_messages(
        self,
        user_id: int,
        limit: int = 8,
    ) -> list[aiosqlite.Row]:
        rows = await self._fetch_latest(
            """
            SELECT role, text, created_at
            FROM conversation_messages
            WHERE user_id = ?
            ORDER BY created_at DESC, id DESC
            LIMIT ?
            """,
            user_id,
            limit,
        )
        return list(reversed(rows))

    async def _execute_write(self, query: str, params: tuple[Any, ...]) -> None:
        db = self._db()
        await db.execute(query, params)
        await db.commit()

    async def _fetch_latest(
        self,
        query: str,
        user_id: int,
        limit: int,
    ) -> list[aiosqlite.Row]:
        db = self._db()
        async with db.execute(query, (user_id, limit)) as cursor:
            rows = await cursor.fetchall()
        return list(rows)

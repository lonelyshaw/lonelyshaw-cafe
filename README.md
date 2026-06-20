# Lonelyroom Telegram Bot

Lonelyroom — уютная цифровая комната в Telegram.

Слоганы:

- "каждый человек — это целая комната."
- "познакомься с собой заново."

Стек:

- Python 3.11+
- aiogram 3
- SQLite

## Что умеет бот

Главное меню:

- 🏡 Моя комната
- 📖 Книга обо мне
- 🌙 Вопрос дня
- ✨ Сохранить момент
- 💌 Письма
- ☕ Собери мне вечер
- 🤍 Поговорить

Интерфейс полностью на русском.
Сообщения короткие, спокойные и теплые.
Режимов персонажа нет.

## Структура проекта

```text
.
├── lonelyroom_bot/
│   ├── __init__.py
│   ├── config.py
│   ├── database.py
│   ├── handlers.py
│   ├── keyboards.py
│   ├── main.py
│   ├── states.py
│   └── texts.py
├── docs/
│   └── product_specification.md
├── sql/
│   └── schema.sql
├── .env.example
├── .gitignore
├── requirements.txt
└── README.md
```

## База данных

SQLite-файл создается автоматически при первом запуске.

По умолчанию путь такой:

```text
data/lonelyroom.sqlite3
```

Схема находится в:

```text
sql/schema.sql
```

Основные таблицы:

- `users` — пользователи Telegram;
- `book_entries` — страницы книги о себе;
- `daily_answers` — ответы на вопрос дня;
- `moments` — сохраненные моменты;
- `letters` — письма себе.

## Локальный запуск

### 1. Создайте бота в Telegram

Откройте `@BotFather`, создайте бота и получите токен.

### 2. Создайте виртуальное окружение

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Установите зависимости

```bash
pip install -r requirements.txt
```

### 4. Создайте `.env`

```bash
cp .env.example .env
```

Откройте `.env` и вставьте токен:

```env
BOT_TOKEN=ваш_токен_от_BotFather
DATABASE_PATH=data/lonelyroom.sqlite3
```

### 5. Запустите бота

```bash
python -m lonelyroom_bot.main
```

После запуска напишите боту `/start`.

## Команды

- `/start` — открыть Lonelyroom;
- `/menu` — вернуться в главное меню.

## Настройка

Переменные окружения:

| Переменная | Описание |
| --- | --- |
| `BOT_TOKEN` | токен Telegram-бота |
| `DATABASE_PATH` | путь к SQLite-файлу |

## Важно

Проект рассчитан на запуск на вашем компьютере.
Replit не используется.

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

CREATE TABLE IF NOT EXISTS moods (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    mood_date TEXT NOT NULL,
    mood TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE (user_id, mood_date)
);

CREATE TABLE IF NOT EXISTS user_pets (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    pet_code TEXT NOT NULL,
    name TEXT NOT NULL,
    description TEXT NOT NULL,
    unlocked_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE,
    UNIQUE (user_id, pet_code)
);

CREATE TABLE IF NOT EXISTS mirror_entries (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    text TEXT NOT NULL,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS room_profiles (
    user_id INTEGER PRIMARY KEY,
    room_nickname TEXT UNIQUE,
    room_privacy TEXT NOT NULL DEFAULT 'private',
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    updated_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS room_notes (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_owner_id INTEGER NOT NULL,
    guest_user_id INTEGER NOT NULL,
    guest_room_nickname TEXT,
    text TEXT NOT NULL,
    is_read INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_owner_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (guest_user_id) REFERENCES users(id) ON DELETE CASCADE
);

CREATE TABLE IF NOT EXISTS room_lights (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    room_owner_id INTEGER NOT NULL,
    guest_user_id INTEGER NOT NULL,
    is_seen INTEGER NOT NULL DEFAULT 0,
    created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY (room_owner_id) REFERENCES users(id) ON DELETE CASCADE,
    FOREIGN KEY (guest_user_id) REFERENCES users(id) ON DELETE CASCADE
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

CREATE INDEX IF NOT EXISTS idx_moods_user_date
    ON moods (user_id, mood_date DESC);

CREATE INDEX IF NOT EXISTS idx_user_pets_user_unlocked
    ON user_pets (user_id, unlocked_at DESC);

CREATE INDEX IF NOT EXISTS idx_mirror_entries_user_created
    ON mirror_entries (user_id, created_at DESC, id DESC);

CREATE UNIQUE INDEX IF NOT EXISTS idx_room_profiles_nickname
    ON room_profiles (room_nickname)
    WHERE room_nickname IS NOT NULL;

CREATE INDEX IF NOT EXISTS idx_room_notes_owner_created
    ON room_notes (room_owner_id, created_at DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_room_notes_owner_unread
    ON room_notes (room_owner_id, is_read, created_at DESC);

CREATE INDEX IF NOT EXISTS idx_room_lights_owner_created
    ON room_lights (room_owner_id, created_at DESC, id DESC);

CREATE INDEX IF NOT EXISTS idx_room_lights_owner_unseen
    ON room_lights (room_owner_id, is_seen, created_at DESC);

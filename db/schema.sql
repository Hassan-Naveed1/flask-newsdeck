-- Schema for storing fetched news articles and saved favorites.

CREATE TABLE IF NOT EXISTS articles (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    topic TEXT NOT NULL,                    -- Topic label: tech|business|sports
    title TEXT NOT NULL,                    -- Article headline
    source TEXT,                            -- Source or publisher name
    url TEXT UNIQUE,                        -- Canonical article URL
    image_url TEXT,                         -- Optional image link
    published_at TEXT,                      -- Source publish timestamp
    fetched_at TEXT                         -- When it was retrieved
);

CREATE TABLE IF NOT EXISTS favorites (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    article_id INTEGER UNIQUE,              -- Links back to the article
    saved_at TEXT                           -- Timestamp when it was saved
);

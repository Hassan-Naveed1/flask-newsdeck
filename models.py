# Database access and helper functions.
import os
import sqlite3

# Database and schema file locations.
DB_PATH = os.path.join(os.path.dirname(__file__), "db", "news.db")
SCHEMA_PATH = os.path.join(os.path.dirname(__file__), "db", "schema.sql")

def _connect():
    """Opens a SQLite connection with dict-like row access."""
    conn = sqlite3.connect(DB_PATH, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn

def init_db():
    """Ensures the database file and schema exist."""
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)
    with _connect() as conn, open(SCHEMA_PATH, "r", encoding="utf-8") as f:
        conn.executescript(f.read())
        conn.commit()

def upsert_articles(items: list[dict]) -> tuple[int, int]:
    """Inserts new articles (skips duplicates by URL)."""
    inserted, updated = 0, 0
    with _connect() as conn:
        cur = conn.cursor()
        for a in items:
            cur.execute(
                """
                INSERT OR IGNORE INTO articles(topic, title, source, url, image_url, published_at, fetched_at)
                VALUES(?,?,?,?,?,?,?)
                """,
                (
                    a.get("topic"),
                    a.get("title"),
                    a.get("source"),
                    a.get("url"),
                    a.get("image_url"),
                    a.get("published_at"),
                    a.get("fetched_at"),
                ),
            )
            if cur.rowcount == 1:
                inserted += 1
        conn.commit()
    return inserted, updated

def list_articles(topic: str | None, page: int, limit: int) -> tuple[list[dict], int]:
    """Fetches paginated articles, optionally filtered by topic."""
    where = []
    params = []
    if topic:
        where.append("topic = ?")
        params.append(topic)

    where_sql = ("WHERE " + " AND ".join(where)) if where else ""
    offset = (page - 1) * limit

    with _connect() as conn:
        total = conn.execute(f"SELECT COUNT(*) AS c FROM articles {where_sql}", params).fetchone()["c"]
        rows = conn.execute(
            f"""
            SELECT id, topic, title, source, url, image_url, published_at, fetched_at
            FROM articles {where_sql}
            ORDER BY datetime(published_at) DESC, id DESC
            LIMIT ? OFFSET ?
            """,
            (*params, limit, offset),
        ).fetchall()

    return [dict(r) for r in rows], int(total)

def add_favorite(article_id: int):
    """Adds an article to the favorites list."""
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute(
            """
            INSERT OR IGNORE INTO favorites(article_id, saved_at)
            VALUES(?, datetime('now'))
            """,
            (article_id,),
        )
        conn.commit()
        return cur.lastrowid or None

def list_favorites() -> list[dict]:
    """Returns all favorites joined with article details."""
    with _connect() as conn:
        rows = conn.execute(
            """
            SELECT f.id,
                   a.id AS article_id,
                   a.title,
                   a.source,
                   a.url,
                   a.published_at,
                   f.saved_at
            FROM favorites f
            JOIN articles a ON a.id = f.article_id
            ORDER BY datetime(f.saved_at) DESC
            """
        ).fetchall()
    return [dict(r) for r in rows]

def delete_favorite(article_id: int) -> int:
    """Deletes a favorite entry by its article_id."""
    with _connect() as conn:
        cur = conn.cursor()
        cur.execute("DELETE FROM favorites WHERE article_id = ?", (article_id,))
        conn.commit()
        return cur.rowcount

import aiosqlite
from typing import List, Dict, Any


async def _ensure_migrations(db: aiosqlite.Connection):
    # Ensure reminder columns exist
    await db.execute("""
        CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            subscribed INTEGER DEFAULT 0,
            joined_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Check existing columns
    async with db.execute("PRAGMA table_info(users)") as cursor:
        cols = [row[1] async for row in cursor]
    if "reminder1_sent" not in cols:
        await db.execute("ALTER TABLE users ADD COLUMN reminder1_sent INTEGER DEFAULT 0")
    if "reminder2_sent" not in cols:
        await db.execute("ALTER TABLE users ADD COLUMN reminder2_sent INTEGER DEFAULT 0")
    if "reminder3_sent" not in cols:
        await db.execute("ALTER TABLE users ADD COLUMN reminder3_sent INTEGER DEFAULT 0")
    if "reminder4_sent" not in cols:
        await db.execute("ALTER TABLE users ADD COLUMN reminder4_sent INTEGER DEFAULT 0")


async def init_db():
    async with aiosqlite.connect("bot.db") as db:
        await _ensure_migrations(db)
        await db.commit()


async def add_user(user_id: int):
    async with aiosqlite.connect("bot.db") as db:
        await _ensure_migrations(db)
        await db.execute("INSERT OR IGNORE INTO users (user_id) VALUES (?)", (user_id,))
        await db.commit()


async def update_subscription(user_id: int, subscribed: bool):
    async with aiosqlite.connect("bot.db") as db:
        await _ensure_migrations(db)
        await db.execute("UPDATE users SET subscribed = ? WHERE user_id = ?", (1 if subscribed else 0, user_id))
        await db.commit()


async def get_all_users() -> List[aiosqlite.Row]:
    db = await aiosqlite.connect("bot.db")
    db.row_factory = aiosqlite.Row
    await _ensure_migrations(db)
    async with db.execute("SELECT user_id, subscribed, joined_at, reminder1_sent, reminder2_sent, reminder3_sent, reminder4_sent FROM users") as cursor:
        rows = await cursor.fetchall()
    await db.close()
    return rows


async def mark_reminder_sent(user_id: int, step: int):
    if step not in (1, 2, 3, 4):
        return
    column = f"reminder{step}_sent"
    async with aiosqlite.connect("bot.db") as db:
        await _ensure_migrations(db)
        await db.execute(f"UPDATE users SET {column} = 1 WHERE user_id = ?", (user_id,))
        await db.commit()

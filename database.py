import aiosqlite
import logging

logger = logging.getLogger(__name__)

DB_PATH = "subscriptions.db"

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''
            CREATE TABLE IF NOT EXISTS subscribers (
                chat_id INTEGER PRIMARY KEY
            )
        ''')
        await db.commit()
    logger.info("Database initialized.")

async def add_subscriber(chat_id: int) -> bool:
    """Add a user to the subscription list. Returns True if added, False if already exists."""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            await db.execute("INSERT INTO subscribers (chat_id) VALUES (?)", (chat_id,))
            await db.commit()
            return True
    except aiosqlite.IntegrityError:
        return False  # Already subscribed
    except Exception as e:
        logger.error(f"Error adding subscriber {chat_id}: {e}")
        return False

async def remove_subscriber(chat_id: int) -> bool:
    """Remove a user from the subscription list. Returns True if removed."""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            cursor = await db.execute("DELETE FROM subscribers WHERE chat_id = ?", (chat_id,))
            await db.commit()
            return cursor.rowcount > 0
    except Exception as e:
        logger.error(f"Error removing subscriber {chat_id}: {e}")
        return False

async def get_all_subscribers() -> list[int]:
    """Get all subscribed chat IDs."""
    try:
        async with aiosqlite.connect(DB_PATH) as db:
            async with db.execute("SELECT chat_id FROM subscribers") as cursor:
                rows = await cursor.fetchall()
                return [row[0] for row in rows]
    except Exception as e:
        logger.error(f"Error getting subscribers: {e}")
        return []

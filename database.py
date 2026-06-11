import asyncpg
import logging
import os

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
_pool = None

async def get_pool():
    global _pool
    if _pool is None and DATABASE_URL:
        _pool = await asyncpg.create_pool(DATABASE_URL)
    return _pool

async def init_db():
    pool = await get_pool()
    if not pool:
        logger.error("DATABASE_URL not set. Skipping DB init.")
        return
    try:
        async with pool.acquire() as conn:
            await conn.execute('''
                CREATE TABLE IF NOT EXISTS subscribers (
                    chat_id BIGINT PRIMARY KEY
                )
            ''')
        logger.info("Database initialized.")
    except Exception as e:
        logger.error(f"Failed to init DB: {e}")

async def add_subscriber(chat_id: int) -> bool:
    pool = await get_pool()
    if not pool: return False
    try:
        async with pool.acquire() as conn:
            await conn.execute("INSERT INTO subscribers (chat_id) VALUES ($1)", chat_id)
            return True
    except asyncpg.exceptions.UniqueViolationError:
        return False
    except Exception as e:
        logger.error(f"Error adding subscriber {chat_id}: {e}")
        return False

async def remove_subscriber(chat_id: int) -> bool:
    pool = await get_pool()
    if not pool: return False
    try:
        async with pool.acquire() as conn:
            result = await conn.execute("DELETE FROM subscribers WHERE chat_id = $1", chat_id)
            return int(result.split()[-1]) > 0
    except Exception as e:
        logger.error(f"Error removing subscriber {chat_id}: {e}")
        return False

async def get_all_subscribers() -> list[int]:
    pool = await get_pool()
    if not pool: return []
    try:
        async with pool.acquire() as conn:
            rows = await conn.fetch("SELECT chat_id FROM subscribers")
            return [row['chat_id'] for row in rows]
    except Exception as e:
        logger.error(f"Error getting subscribers: {e}")
        return []

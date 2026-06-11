import asyncpg
import logging
import os
import asyncio
import urllib.parse
from datetime import datetime
import pytz
import aiohttp
from dotenv import load_dotenv

# Load environment variables internally to avoid import-order issues in other entrypoints
load_dotenv()

logger = logging.getLogger(__name__)

DATABASE_URL = os.getenv("DATABASE_URL")
if DATABASE_URL:
    DATABASE_URL = DATABASE_URL.strip().strip("'\"")

_pool = None
_pool_lock = asyncio.Lock()

# Cache version to automatically invalidate older caches on design updates
CACHE_VERSION = "v3"

# Global flag to track if the pgvector/topic_embedding column is supported and available in the database
HAS_VECTOR_COLUMN = True

_session = None
_session_lock = asyncio.Lock()

async def get_http_session() -> aiohttp.ClientSession:
    global _session
    async with _session_lock:
        if _session is None or _session.closed:
            _session = aiohttp.ClientSession()
        return _session

async def get_pool():
    global _pool
    async with _pool_lock:
        if _pool is None and DATABASE_URL:
            try:
                parsed = urllib.parse.urlparse(DATABASE_URL)
                # Parse query parameters for sslmode
                query_params = urllib.parse.parse_qs(parsed.query)
                ssl_mode = query_params.get('sslmode', ['prefer'])[0]
                
                # Safely decode username and password
                user = urllib.parse.unquote(parsed.username) if parsed.username else None
                password = urllib.parse.unquote(parsed.password) if parsed.password else None
                host = parsed.hostname
                port = parsed.port or 5432
                database_name = parsed.path.lstrip('/')
                
                logger.info(f"Connecting to database host: '{host}' (port: {port}, database: '{database_name}')")
                
                _pool = await asyncpg.create_pool(
                    host=host,
                    port=port,
                    user=user,
                    password=password,
                    database=database_name,
                    ssl=ssl_mode if ssl_mode != 'disable' else None
                )
            except Exception as e:
                logger.error(f"Failed to connect with parsed params: {e}. Falling back to raw DSN.")
                _pool = await asyncpg.create_pool(DATABASE_URL)
    return _pool

async def init_db():
    global HAS_VECTOR_COLUMN
    pool = await get_pool()
    if pool is None:
        logger.warning("Database connection pool is None. Database remains offline.")
        return
    try:
        async with pool.acquire() as conn:
            try:
                await conn.execute("CREATE EXTENSION IF NOT EXISTS vector;")
            except Exception as e:
                logger.warning(f"Could not enable pgvector extension (non-critical): {e}")
                
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS subscribers (
                    chat_id BIGINT PRIMARY KEY,
                    joined_at TIMESTAMP WITH TIME ZONE DEFAULT CURRENT_TIMESTAMP
                )
            """)
            await conn.execute("""
                CREATE TABLE IF NOT EXISTS digests_cache (
                    topic TEXT PRIMARY KEY,
                    file_id TEXT NOT NULL,
                    generated_date_ist DATE NOT NULL
                )
            """)
            try:
                await conn.execute("ALTER TABLE digests_cache ADD COLUMN IF NOT EXISTS topic_embedding vector(384);")
                # Verify that the column was successfully added/exists
                col_check = await conn.fetchrow("""
                    SELECT column_name FROM information_schema.columns 
                    WHERE table_name = 'digests_cache' AND column_name = 'topic_embedding'
                """)
                if not col_check:
                    logger.warning("topic_embedding column missing from database schema. Vector/semantic caching disabled.")
                    HAS_VECTOR_COLUMN = False
                else:
                    HAS_VECTOR_COLUMN = True
            except Exception as e:
                logger.warning(f"Could not add topic_embedding column (vector extension may be unsupported): {e}. Vector/semantic caching disabled.")
                HAS_VECTOR_COLUMN = False
                
            logger.info(f"Database tables initialized. HAS_VECTOR_COLUMN: {HAS_VECTOR_COLUMN}")
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

async def close_db():
    global _pool, _session
    if _pool:
        await _pool.close()
        _pool = None
        logger.info("Database connection pool closed.")
    if _session and not _session.closed:
        await _session.close()
        _session = None
        logger.info("HTTP client session closed.")

def get_current_ist_date():
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist).date()

async def get_embedding(text: str) -> list[float] | None:
    url = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
    headers = {}
    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        headers["Authorization"] = f"Bearer {hf_token}"
    
    try:
        session = await get_http_session()
        async with session.post(url, headers=headers, json={"inputs": text}) as response:
            if response.status == 200:
                data = await response.json()
                # HF API can return a list of floats or a list of list of floats
                if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
                    return data[0]
                elif isinstance(data, list) and len(data) > 0:
                    return data
            else:
                text_resp = await response.text()
                logger.error(f"HuggingFace embedding failed ({response.status}): {text_resp}")
    except Exception as e:
        logger.error(f"Error fetching embedding from HuggingFace: {e}")
    return None

async def get_cached_file_id_exact(topic: str) -> str | None:
    pool = await get_pool()
    if pool is None: return None
    
    versioned_topic = f"{CACHE_VERSION}:{topic}"
    current_ist_date = get_current_ist_date()
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT file_id FROM digests_cache 
                WHERE topic = $1 AND generated_date_ist::DATE = $2::DATE
            """, versioned_topic, current_ist_date)
            if row:
                return row['file_id']
    except Exception as e:
        logger.error(f"Error reading exact cache: {e}")
    return None

async def set_cached_file_id_exact(topic: str, file_id: str):
    pool = await get_pool()
    if pool is None: return
    
    versioned_topic = f"{CACHE_VERSION}:{topic}"
    current_ist_date = get_current_ist_date()
    try:
        async with pool.acquire() as conn:
            if HAS_VECTOR_COLUMN:
                await conn.execute("""
                    INSERT INTO digests_cache (topic, file_id, generated_date_ist)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (topic) DO UPDATE 
                    SET file_id = EXCLUDED.file_id,
                        generated_date_ist = EXCLUDED.generated_date_ist,
                        topic_embedding = NULL
                """, versioned_topic, file_id, current_ist_date)
            else:
                await conn.execute("""
                    INSERT INTO digests_cache (topic, file_id, generated_date_ist)
                    VALUES ($1, $2, $3)
                    ON CONFLICT (topic) DO UPDATE 
                    SET file_id = EXCLUDED.file_id,
                        generated_date_ist = EXCLUDED.generated_date_ist
                """, versioned_topic, file_id, current_ist_date)
    except Exception as e:
        logger.error(f"Error writing exact cache: {e}")

async def get_cached_file_id_semantic(topic: str, threshold: float = 0.85) -> str | None:
    pool = await get_pool()
    if pool is None: return None
    
    if not HAS_VECTOR_COLUMN:
        logger.info(f"Vector support disabled. Falling back to exact match for topic: '{topic}'")
        return await get_cached_file_id_exact(topic)
        
    embedding = await get_embedding(topic)
    if not embedding:
        return await get_cached_file_id_exact(topic)
        
    current_ist_date = get_current_ist_date()
    vec_str = str(embedding)
    try:
        async with pool.acquire() as conn:
            row = await conn.fetchrow("""
                SELECT file_id, 1 - (topic_embedding <=> $1::vector) as similarity
                FROM digests_cache
                WHERE generated_date_ist::DATE = $2::DATE
                  AND topic LIKE $4
                  AND topic_embedding IS NOT NULL
                  AND 1 - (topic_embedding <=> $1::vector) >= $3
                ORDER BY similarity DESC
                LIMIT 1
            """, vec_str, current_ist_date, threshold, f"{CACHE_VERSION}:%")
            
            if row:
                logger.info(f"Semantic cache hit for '{topic}' with similarity: {row['similarity']:.3f}")
                return row['file_id']
    except Exception as e:
        logger.error(f"Error reading semantic cache: {e}")
    return None

async def set_cached_file_id_semantic(topic: str, file_id: str):
    pool = await get_pool()
    if pool is None: return
    
    if not HAS_VECTOR_COLUMN:
        await set_cached_file_id_exact(topic, file_id)
        return
        
    embedding = await get_embedding(topic)
    if not embedding:
        await set_cached_file_id_exact(topic, file_id)
        return
        
    current_ist_date = get_current_ist_date()
    vec_str = str(embedding)
    versioned_topic = f"{CACHE_VERSION}:{topic}"
    try:
        async with pool.acquire() as conn:
            await conn.execute("""
                INSERT INTO digests_cache (topic, file_id, generated_date_ist, topic_embedding)
                VALUES ($1, $2, $3, $4::vector)
                ON CONFLICT (topic) DO UPDATE 
                SET file_id = EXCLUDED.file_id,
                    generated_date_ist = EXCLUDED.generated_date_ist,
                    topic_embedding = EXCLUDED.topic_embedding
            """, versioned_topic, file_id, current_ist_date, vec_str)
    except Exception as e:
        logger.error(f"Error writing semantic cache: {e}")

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
CACHE_VERSION = "v4"

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
                
            logger.info(f"[DB] Database tables initialized. HAS_VECTOR_COLUMN: {HAS_VECTOR_COLUMN}")
    except Exception as e:
        logger.error(f"Failed to init DB: {e}")

async def execute_with_retry(query: str, *args, is_fetch: bool = False, is_fetchrow: bool = False):
    """Executes a query or fetches rows with retries and auto-reconnection on transient errors."""
    if not DATABASE_URL:
        raise asyncpg.exceptions.InterfaceError("DATABASE_URL is not set. Database remains offline.")
        
    last_err = None
    for attempt in range(3):
        try:
            pool = await get_pool()
            if pool is None:
                # Force pool recreation if None or failed to initialize
                global _pool
                async with _pool_lock:
                    _pool = None
                pool = await get_pool()
                if pool is None:
                    raise asyncpg.exceptions.InterfaceError("Could not establish connection pool.")
            
            async with pool.acquire() as conn:
                if is_fetchrow:
                    return await conn.fetchrow(query, *args)
                elif is_fetch:
                    return await conn.fetch(query, *args)
                else:
                    return await conn.execute(query, *args)
        except (asyncpg.exceptions.InterfaceError, asyncpg.exceptions.InternalClientError) as e:
            last_err = e
            logger.warning(f"Transient DB connection error on attempt {attempt + 1}/3: {e}")
            # Reset pool to force reconnection on next retry
            async with _pool_lock:
                if _pool:
                    try:
                        await _pool.close()
                    except Exception:
                        pass
                    _pool = None
            if attempt < 2:
                await asyncio.sleep(2 ** attempt)
        except Exception as e:
            last_err = e
            logger.warning(f"Database query error on attempt {attempt + 1}/3: {e}")
            if attempt < 2:
                await asyncio.sleep(2 ** attempt)
            else:
                raise e
    if last_err:
        raise last_err
    raise RuntimeError("Database operation failed after 3 attempts.")

async def add_subscriber(chat_id: int) -> bool:
    try:
        await execute_with_retry("INSERT INTO subscribers (chat_id) VALUES ($1)", chat_id)
        return True
    except asyncpg.exceptions.UniqueViolationError:
        return False
    except Exception as e:
        logger.error(f"Error adding subscriber {chat_id}: {e}")
        return False

async def remove_subscriber(chat_id: int) -> bool:
    try:
        result = await execute_with_retry("DELETE FROM subscribers WHERE chat_id = $1", chat_id)
        return int(result.split()[-1]) > 0
    except Exception as e:
        logger.error(f"Error removing subscriber {chat_id}: {e}")
        return False

async def is_subscriber(chat_id: int) -> bool:
    """Check if a user is subscribed."""
    try:
        rows = await execute_with_retry("SELECT 1 FROM subscribers WHERE chat_id = $1", chat_id, is_fetch=True)
        return len(rows) > 0
    except Exception as e:
        logger.error(f"Error checking subscriber {chat_id}: {e}")
        return False

async def get_all_subscribers() -> list[int]:
    try:
        rows = await execute_with_retry("SELECT chat_id FROM subscribers", is_fetch=True)
        return [row['chat_id'] for row in rows]
    except Exception as e:
        logger.error(f"Error getting subscribers: {e}")
        return []

async def close_db():
    global _pool, _session
    if _pool:
        try:
            await _pool.close()
        except Exception as e:
            logger.warning(f"Error closing DB pool: {e}")
        _pool = None
        logger.info("Database connection pool closed.")
    if _session and not _session.closed:
        await _session.close()
        _session = None
        logger.info("HTTP client session closed.")

def get_current_ist_date():
    ist = pytz.timezone('Asia/Kolkata')
    return datetime.now(ist).date()

# Local memory cache to prevent redundant HF API calls for identical texts
_hf_embedding_cache = {}

async def get_embedding(text: str) -> list[float] | None:
    if text in _hf_embedding_cache:
        return _hf_embedding_cache[text]
        
    url = "https://api-inference.huggingface.co/models/sentence-transformers/all-MiniLM-L6-v2"
    headers = {}
    hf_token = os.getenv("HF_TOKEN")
    if hf_token:
        headers["Authorization"] = f"Bearer {hf_token}"
    
    for attempt in range(3):
        try:
            session = await get_http_session()
            payload = {
                "inputs": text,
                "options": {"wait_for_model": True, "use_cache": True}
            }
            async with session.post(url, headers=headers, json=payload, timeout=20) as response:
                if response.status == 200:
                    data = await response.json()
                    # Check if Hugging Face returned an error indicating the model is loading
                    if isinstance(data, dict) and "error" in data:
                        err_msg = data.get("error", "")
                        if "loading" in err_msg.lower():
                            est_time = min(float(data.get("estimated_time", 5)), 10.0)
                            logger.info(f"HuggingFace model is loading. Waiting {est_time}s (attempt {attempt + 1}/3)...")
                            await asyncio.sleep(est_time)
                            continue
                    
                    if isinstance(data, list) and len(data) > 0 and isinstance(data[0], list):
                        _hf_embedding_cache[text] = data[0]
                        return data[0]
                    elif isinstance(data, list) and len(data) > 0:
                        _hf_embedding_cache[text] = data
                        return data
                elif response.status in (503, 429):
                    logger.warning(f"HuggingFace transient status {response.status} (attempt {attempt + 1}/3). Retrying after 3s...")
                    await asyncio.sleep(3)
                else:
                    text_resp = await response.text()
                    logger.error(f"HuggingFace embedding failed ({response.status}): {text_resp}")
                    break
        except aiohttp.ClientConnectorError as e:
            logger.warning(f"HuggingFace connection/DNS error: {e}. Skipping embedding query.")
            return None
        except Exception as e:
            logger.error(f"Error fetching embedding from HuggingFace (attempt {attempt + 1}/3): {e}")
            if attempt < 2:
                await asyncio.sleep(3)
    return None

async def get_cached_file_id_exact(topic: str) -> str | None:
    versioned_topic = f"{CACHE_VERSION}:{topic}"
    current_ist_date = get_current_ist_date()
    try:
        row = await execute_with_retry("""
            SELECT file_id, generated_date_ist FROM digests_cache 
            WHERE topic = $1 AND generated_date_ist::DATE = $2::DATE
        """, versioned_topic, current_ist_date, is_fetchrow=True)
        if row:
            logger.info(f"[DB] Exact cache hit for '{topic}' (Date: {row['generated_date_ist']})")
            return row['file_id']
        logger.info(f"[DB] Exact cache miss for '{topic}'")
    except Exception as e:
        logger.error(f"Error reading exact cache: {e}")
    return None

async def set_cached_file_id_exact(topic: str, file_id: str):
    versioned_topic = f"{CACHE_VERSION}:{topic}"
    current_ist_date = get_current_ist_date()
    try:
        if HAS_VECTOR_COLUMN:
            await execute_with_retry("""
                INSERT INTO digests_cache (topic, file_id, generated_date_ist)
                VALUES ($1, $2, $3)
                ON CONFLICT (topic) DO UPDATE 
                SET file_id = EXCLUDED.file_id,
                    generated_date_ist = EXCLUDED.generated_date_ist,
                    topic_embedding = NULL
            """, versioned_topic, file_id, current_ist_date)
        else:
            await execute_with_retry("""
                INSERT INTO digests_cache (topic, file_id, generated_date_ist)
                VALUES ($1, $2, $3)
                ON CONFLICT (topic) DO UPDATE 
                SET file_id = EXCLUDED.file_id,
                    generated_date_ist = EXCLUDED.generated_date_ist
            """, versioned_topic, file_id, current_ist_date)
    except Exception as e:
        logger.error(f"Error writing exact cache: {e}")

async def get_cached_file_id_semantic(topic: str, threshold: float = 0.85) -> str | None:
    if not HAS_VECTOR_COLUMN:
        logger.info(f"[DB] Vector support disabled. Falling back to exact match for topic: '{topic}'")
        return await get_cached_file_id_exact(topic)
        
    embedding = await get_embedding(topic)
    if not embedding:
        return await get_cached_file_id_exact(topic)
        
    current_ist_date = get_current_ist_date()
    vec_str = str(embedding)
    try:
        row = await execute_with_retry("""
            SELECT file_id, 1 - (topic_embedding <=> $1::vector) as similarity
            FROM digests_cache
            WHERE generated_date_ist::DATE = $2::DATE
              AND topic LIKE $4
              AND topic_embedding IS NOT NULL
              AND 1 - (topic_embedding <=> $1::vector) >= $3
            ORDER BY similarity DESC
            LIMIT 1
        """, vec_str, current_ist_date, threshold, f"{CACHE_VERSION}:%", is_fetchrow=True)
        
        if row:
            logger.info(f"[DB] Semantic cache hit for '{topic}' with similarity: {row['similarity']:.3f}")
            return row['file_id']
    except Exception as e:
        logger.error(f"Error reading semantic cache: {e}")
    return None

async def set_cached_file_id_semantic(topic: str, file_id: str):
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
        await execute_with_retry("""
            INSERT INTO digests_cache (topic, file_id, generated_date_ist, topic_embedding)
            VALUES ($1, $2, $3, $4::vector)
            ON CONFLICT (topic) DO UPDATE 
            SET file_id = EXCLUDED.file_id,
                generated_date_ist = EXCLUDED.generated_date_ist,
                topic_embedding = EXCLUDED.topic_embedding
        """, versioned_topic, file_id, current_ist_date, vec_str)
    except Exception as e:
        logger.error(f"Error writing semantic cache: {e}")

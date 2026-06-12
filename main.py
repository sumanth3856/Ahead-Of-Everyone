import os
import logging
import json
import time
import asyncio
from dotenv import load_dotenv

# Initialize config/logging
import config
from scraper import fetch_dynamic_news, register_sent_stories, fetch_targeted_news
from pdf_generator import generate_digest_pdf
from telegram_client import send_pdf_to_telegram

logger = logging.getLogger(__name__)

async def generate_latest_digest(limit=5, progress_callback=None) -> str | None:
    logger.info("Generating latest digest...")
    try:
        if progress_callback:
            progress_callback("Finding Stories", 5, "Connecting to news feeds to fetch daily articles...")
        stories = await fetch_dynamic_news(limit, progress_callback)
        pdf_filename = generate_digest_pdf(stories, progress_callback=progress_callback)
        if not pdf_filename:
            logger.error("No stories scraped or generated.")
            return None
        try:
            register_sent_stories(stories)
        except Exception as reg_err:
            logger.error(f"Failed to register sent stories: {reg_err}")
        return pdf_filename
    except Exception as e:
        logger.error(f"Error during latest digest generation: {e}", exc_info=True)
        return None

CACHE_FILE = "query_cache.json"
CACHE_TTL = 24 * 3600  # 24 hours

def load_query_cache() -> dict:
    if os.path.exists(CACHE_FILE):
        try:
            with open(CACHE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Failed to load query cache: {e}")
    return {}

def save_query_cache(cache: dict) -> None:
    try:
        with open(CACHE_FILE, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2)
    except Exception as e:
        logger.error(f"Failed to save query cache: {e}")

import string
# Fast C-level translation table to remove punctuation and whitespace
NORM_TRANS = str.maketrans('', '', string.punctuation + string.whitespace)

async def generate_targeted_digest(query: str, limit=5, progress_callback=None) -> str | None:
    logger.info(f"Generating targeted digest for: {query}")
    try:
        cache = load_query_cache()
        # Normalize: exact match only (case-insensitive, strip punctuation/spaces) using ultra-fast translate
        norm_query = query.lower().translate(NORM_TRANS)
        
        if norm_query in cache:
            entry = cache[norm_query]
            if time.time() - entry["timestamp"] < CACHE_TTL:
                pdf_filename = entry["filename"]
                if os.path.exists(pdf_filename):
                    logger.info(f"Cache hit! Returning existing PDF for '{query}'.")
                    if progress_callback:
                        progress_callback("Cache Hit", 100, f"Found recently generated report for '{query}'.", mark_done="Delivering")
                    return pdf_filename
                    
        if progress_callback:
            progress_callback("Finding Stories", 5, f"Scraping news feeds for '{query}'...")
        stories = await fetch_targeted_news(query, limit, progress_callback)
        pdf_filename = generate_digest_pdf(stories, custom_topic=query, progress_callback=progress_callback)
        if not pdf_filename:
            logger.error("No stories scraped or generated.")
            return None
            
        cache[norm_query] = {
            "filename": pdf_filename,
            "timestamp": time.time()
        }
        save_query_cache(cache)
        
        return pdf_filename
    except Exception as e:
        logger.error(f"Error during targeted digest generation: {e}", exc_info=True)
        return None

async def main() -> None:
    logger.info("Starting AoE Tech News execution pipeline (Manual Run).")
    pdf_filename = None
    try:
        pdf_filename = await generate_latest_digest(5)
        if not pdf_filename:
            return
            
        load_dotenv()
        BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8658316403:AAH16J5AC2iGmdzM3LyoUS1-zSf4oavzTF4")
        CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "6038057345")
        
        success = send_pdf_to_telegram(pdf_filename, BOT_TOKEN, CHAT_ID)
        if not success:
            logger.error("Delivery failed. Check logs.")
    except Exception as e:
        logger.error(f"Manual pipeline execution failed: {e}", exc_info=True)
    finally:
        if pdf_filename and os.path.exists(pdf_filename):
            try:
                os.remove(pdf_filename)
                logger.info(f"Cleaned up manual run PDF: {pdf_filename}")
            except Exception as e:
                logger.error(f"Failed to delete {pdf_filename}: {e}")

if __name__ == "__main__":
    asyncio.run(main())

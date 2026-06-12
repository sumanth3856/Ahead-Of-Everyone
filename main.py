import os
import logging
from dotenv import load_dotenv

# Initialize config/logging
import config
from scraper import fetch_dynamic_news, register_sent_stories, fetch_targeted_news
from pdf_generator import generate_digest_pdf
from telegram_client import send_pdf_to_telegram

logger = logging.getLogger(__name__)

def generate_latest_digest(limit=5) -> str | None:
    logger.info("Generating latest digest...")
    try:
        stories = fetch_dynamic_news(limit)
        pdf_filename = generate_digest_pdf(stories)
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

def generate_targeted_digest(query: str, limit=5) -> str | None:
    logger.info(f"Generating targeted digest for: {query}")
    try:
        stories = fetch_targeted_news(query, limit)
        pdf_filename = generate_digest_pdf(stories, custom_topic=query)
        if not pdf_filename:
            logger.error("No stories scraped or generated.")
            return None
        return pdf_filename
    except Exception as e:
        logger.error(f"Error during targeted digest generation: {e}", exc_info=True)
        return None

def main() -> None:
    logger.info("Starting AoE Tech News execution pipeline (Manual Run).")
    pdf_filename = None
    try:
        pdf_filename = generate_latest_digest(5)
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
    main()

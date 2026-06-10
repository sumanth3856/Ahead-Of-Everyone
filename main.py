import os
import shutil
import logging
from datetime import datetime
from dotenv import load_dotenv

# Initialize config/logging
import config
from scraper import fetch_dynamic_news
from pdf_generator import generate_pdf
from telegram_client import send_pdf_to_telegram

logger = logging.getLogger(__name__)

def main() -> None:
    logger.info("Starting AoE Tech News execution pipeline.")
    
    # 1. Fetch data concurrently
    # We let the scraper decide the limit (default 20) so we don't crash the free API
    stories = fetch_dynamic_news(25)
    
    # 2. Generate PDF
    date_str = datetime.now().strftime("%d-%m-%Y")
    pdf_filename = f"AoE Tech News({date_str}).pdf"
    generate_pdf(stories, pdf_filename)
        
    # 3. Deliver payload
    load_dotenv()
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "8658316403:AAH16J5AC2iGmdzM3LyoUS1-zSf4oavzTF4")
    CHAT_ID = os.getenv("TELEGRAM_CHAT_ID", "6038057345")
    
    success = send_pdf_to_telegram(pdf_filename, BOT_TOKEN, CHAT_ID)
    if not success:
        logger.error("Delivery failed. Check logs.")

if __name__ == "__main__":
    main()

import os
import requests
import logging
from datetime import datetime
from config import BRAND_NAME

logger = logging.getLogger(__name__)

def send_pdf_to_telegram(filename: str, bot_token: str, chat_id: str) -> bool:
    """Delivers the payload to Telegram using the provided credentials."""
    logger.info("Sending PDF to Telegram...")
    url = f"https://api.telegram.org/bot{bot_token}/sendDocument"
    try:
        pretty_filename = os.path.basename(filename).replace("_", " ")
        with open(filename, "rb") as file:
            files = {"document": (pretty_filename, file)}
            data = {
                "chat_id": chat_id, 
                "caption": f"📰 *{BRAND_NAME}* | Digest for {datetime.now().strftime('%b %d, %Y')}\n\nInnovating the future, today.",
                "parse_mode": "Markdown"
            }
            response = requests.post(url, data=data, files=files)
            
        if response.status_code == 200:
            logger.info("Successfully delivered PDF to Telegram!")
            return True
        elif response.status_code == 401:
            logger.error("Failed to send PDF: Telegram Bot Token is Unauthorized (401).")
            return False
        else:
            logger.error(f"Failed to send PDF: {response.text}")
            return False
    except Exception as e:
        logger.error(f"Error sending PDF to Telegram: {e}")
        return False

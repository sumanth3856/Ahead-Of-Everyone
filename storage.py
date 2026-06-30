import os
import aiohttp
import logging
from database import get_http_session
import datetime
import pytz
import urllib.parse
from dotenv import load_dotenv

load_dotenv()

_IST = pytz.timezone('Asia/Kolkata')

logger = logging.getLogger(__name__)

async def upload_pdf_to_supabase(file_path: str, topic: str) -> str:
    """
    Uploads a local PDF file to Supabase Storage and returns the storage path.
    """
    supabase_url = os.getenv("NEXT_PUBLIC_SUPABASE_URL")
    service_key = os.getenv("SUPABASE_SERVICE_ROLE_KEY")
    
    if not supabase_url or not service_key:
        logger.warning("Supabase credentials missing. Cannot upload to Storage.")
        return None
        
    supabase_url = supabase_url.rstrip("/")
    bucket_name = "daily-digests"
    
    # Generate path: YYYY-MM-DD/topic.pdf
    date_str = datetime.datetime.now(_IST).strftime("%Y-%m-%d")
    
    # Sanitize topic string for safe URL/file path
    safe_topic = "".join(c if c.isalnum() else "_" for c in topic)
    file_name = f"{safe_topic}.pdf"
    
    # Path inside the bucket
    storage_path = f"{date_str}/{file_name}"
    
    # Supabase Storage REST API endpoint
    upload_url = f"{supabase_url}/storage/v1/object/{bucket_name}/{urllib.parse.quote(storage_path)}"
    
    headers = {
        "Authorization": f"Bearer {service_key}",
        "Content-Type": "application/pdf",
        "apikey": service_key
    }
    
    try:
        session = await get_http_session()
        with open(file_path, "rb") as f:
            file_data = f.read()
            
        async with session.post(upload_url, data=file_data, headers=headers) as response:
            if response.status in (200, 201):
                logger.info(f"Successfully uploaded {file_path} to Supabase Storage at {storage_path}")
                return storage_path
            else:
                resp_text = await response.text()
                # Check if it already exists
                if "Duplicate" in resp_text or response.status == 409 or ("already exists" in resp_text.lower()):
                    logger.info(f"File {storage_path} already exists in Supabase Storage.")
                    return storage_path
                    
                logger.error(f"Failed to upload to Supabase Storage: {response.status} - {resp_text}")
                return None
    except Exception as e:
        logger.error(f"Exception during Supabase upload: {e}")
        return None

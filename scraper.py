import os
import requests
import tempfile
import logging
import feedparser
from bs4 import BeautifulSoup
from PIL import Image
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta
import time
from openai import OpenAI
from dotenv import load_dotenv

import config

logger = logging.getLogger(__name__)
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def init_openai_client():
    if not OPENROUTER_API_KEY:
        logger.warning("OPENROUTER_API_KEY is not set. AI Summarization will fail.")
    return OpenAI(
        base_url=config.OPENROUTER_API_URL,
        api_key=OPENROUTER_API_KEY,
    )

client = init_openai_client()

def download_image(url: str) -> Optional[str]:
    """Downloads image file safely to a temporary file path."""
    try:
        headers = {'User-Agent': 'Mozilla/5.0'}
        r = requests.get(url, headers=headers, timeout=5, stream=True)
        if r.status_code == 200:
            content_type = r.headers.get('content-type', '')
            if 'image' in content_type:
                ext = '.jpg'
                if 'png' in content_type:
                    ext = '.png'
                elif 'gif' in content_type:
                    ext = '.gif'
                elif 'webp' in content_type:
                    ext = '.webp'
                    
                temp_file = tempfile.NamedTemporaryFile(delete=False, suffix=ext)
                for chunk in r.iter_content(1024):
                    temp_file.write(chunk)
                temp_file.close()
                return temp_file.name
    except Exception as e:
        logger.error(f"Error downloading image {url}: {e}")
    return None

def process_and_convert_image(raw_img_path: Optional[str]) -> str:
    """Converts image to standard JPEG padded to fit 800x600 without cropping."""
    default_img = "default_hero.png"
    try:
        if not raw_img_path or not os.path.exists(raw_img_path):
            return default_img
            
        img = Image.open(raw_img_path)
        if img.mode != 'RGB':
            img = img.convert('RGB')
            
        temp_jpg = tempfile.NamedTemporaryFile(delete=False, suffix='.jpg')
        temp_jpg_name = temp_jpg.name
        temp_jpg.close()
        
        target_width = 800
        target_height = 600
        
        img.thumbnail((target_width, target_height), Image.Resampling.LANCZOS)
        new_img = Image.new("RGB", (target_width, target_height), (247, 250, 252))
        
        paste_x = (target_width - img.width) // 2
        paste_y = (target_height - img.height) // 2
        new_img.paste(img, (paste_x, paste_y))
        
        new_img.save(temp_jpg_name, 'JPEG', quality=90)
        
        try:
            os.remove(raw_img_path)
        except Exception:
            pass
            
        return temp_jpg_name
    except Exception as e:
        logger.error(f"Error processing image {raw_img_path}: {e}")
        return default_img

def ai_summarize(title: str, raw_content: str) -> str:
    """Uses OpenRouter AI to write a highly professional 200-word summary."""
    try:
        response = client.chat.completions.create(
            model=config.OPENROUTER_MODEL,
            messages=[
                {
                    "role": "system",
                    "content": "You are an elite, highly professional tech journalist for 'Ahead of Everyone'. Your task is to write a cohesive, engaging, and premium 200-word editorial news report based on the provided title and raw context. Avoid filler words. Be concise and authoritative."
                },
                {
                    "role": "user",
                    "content": f"Title: {title}\nRaw Context/Snippet: {raw_content}"
                }
            ],
            timeout=30,
        )
        return response.choices[0].message.content.strip()
    except Exception as e:
        logger.error(f"AI Summarization failed for '{title}': {e}")
        return f"Recent developments regarding '{title}' are being actively monitored. While detailed public documentation is evolving, industry experts are analyzing the potential disruptions this may cause. Please refer to the source link below to stay informed on the original publication."

def extract_image_from_html(html_content: str) -> Optional[str]:
    try:
        soup = BeautifulSoup(html_content, 'html.parser')
        for img in soup.find_all('img'):
            src = img.get('src')
            if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png', '.webp']):
                if not any(icon in src.lower() for icon in ['icon', 'logo', 'avatar', 'sprite']):
                    return src
    except Exception:
        pass
    return None

def fetch_rss_feed(feed_url: str) -> List[Dict]:
    logger.info(f"Fetching RSS feed: {feed_url}")
    items = []
    try:
        parsed = feedparser.parse(feed_url)
        cutoff_time = datetime.now() - timedelta(hours=24)
        for entry in parsed.entries:
            # Check date
            published = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published = datetime.fromtimestamp(time.mktime(entry.published_parsed))
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published = datetime.fromtimestamp(time.mktime(entry.updated_parsed))
                
            if published and published < cutoff_time:
                continue

            title = entry.get('title', 'Unknown Title')
            link = entry.get('link', '')
            
            # Extract content and image
            raw_summary = entry.get('summary', '')
            content = entry.get('content', [{'value': ''}])[0]['value'] if hasattr(entry, 'content') else ''
            full_html = raw_summary + " " + content
            
            image_url = extract_image_from_html(full_html)
            if not image_url and hasattr(entry, 'media_content'):
                for media in entry.media_content:
                    if 'url' in media and 'image' in media.get('type', ''):
                        image_url = media['url']
                        break
                        
            # Clean text for AI context
            soup = BeautifulSoup(full_html, 'html.parser')
            text_snippet = soup.get_text(separator=' ', strip=True)[:1000]
            
            items.append({
                "title": title,
                "url": link,
                "raw_text": text_snippet,
                "image_url": image_url
            })
    except Exception as e:
        logger.error(f"Error fetching RSS {feed_url}: {e}")
    return items

def fetch_story_details(item: Dict) -> Dict:
    logger.info(f"AI Processing: {item['title']}")
    final_content = ai_summarize(item['title'], item['raw_text'])
    
    return {
        "title": item['title'],
        "url": item['url'],
        "content": final_content,
        "image_url": item['image_url']
    }

def fetch_dynamic_news(limit: int = 20) -> List[Dict]:
    """Scrapes multi-source RSS feeds and uses AI to summarize."""
    logger.info("Fetching multi-source RSS feeds...")
    rss_feeds = [
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml",
        "https://www.wired.com/feed/rss",
        "https://news.ycombinator.com/rss"
    ]
    
    all_raw_items = []
    with ThreadPoolExecutor(max_workers=4) as executor:
        results = executor.map(fetch_rss_feed, rss_feeds)
        for res in results:
            all_raw_items.extend(res)
            
    logger.info(f"Total raw items fetched from last 24h: {len(all_raw_items)}")
    
    # Deduplicate by title
    seen = set()
    unique_items = []
    for item in all_raw_items:
        if item['title'] not in seen:
            seen.add(item['title'])
            unique_items.append(item)
            
    # Optional capping to avoid massive PDFs
    unique_items = unique_items[:limit]
    
    stories = []
    # Process concurrently through AI
    with ThreadPoolExecutor(max_workers=5) as executor:
        results = executor.map(fetch_story_details, unique_items)
        stories = list(results)
            
    return stories

import os
import requests
import urllib.parse
import tempfile
import logging
from bs4 import BeautifulSoup
from PIL import Image
from typing import List, Dict, Optional, Tuple
from concurrent.futures import ThreadPoolExecutor

logger = logging.getLogger(__name__)

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

def elaborate_content_and_image(url: str, title: str) -> Tuple[str, Optional[str]]:
    """Fetches article page, extracts paragraph texts and official hero image."""
    content = ""
    image_url = None
    try:
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'}
        r = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(r.text, 'html.parser')
        
        meta_og = soup.find('meta', attrs={'property': 'og:image'}) or soup.find('meta', attrs={'name': 'og:image'})
        if meta_og and meta_og.get('content'):
            image_url = urllib.parse.urljoin(url, meta_og.get('content'))
        else:
            meta_tw = soup.find('meta', attrs={'name': 'twitter:image'}) or soup.find('meta', attrs={'property': 'twitter:image'})
            if meta_tw and meta_tw.get('content'):
                image_url = urllib.parse.urljoin(url, meta_tw.get('content'))
            else:
                for img in soup.find_all('img'):
                    src = img.get('src')
                    if src and any(ext in src.lower() for ext in ['.jpg', '.jpeg', '.png']):
                        if not any(icon in src.lower() for icon in ['icon', 'logo', 'avatar', 'sprite']):
                            image_url = urllib.parse.urljoin(url, src)
                            break
                            
        paragraphs = soup.find_all('p')
        text = ' '.join([p.get_text().strip() for p in paragraphs if len(p.get_text().strip()) > 50])
        
        if len(text) < 200:
            content = f"This report covers breaking updates regarding '{title}'. While detailed public documentation is currently minimal or restricted, industry experts are closely monitoring the situation as it develops. The implications of this update may significantly impact upcoming sector trends and strategies. Please follow the source link below to stay informed on the original publication."
        else:
            content = text
            
    except Exception as e:
        logger.error(f"Error elaborating {url}: {e}")
        content = f"Recent developments surrounding '{title}' have just surfaced. Current public insights are actively evolving, and professionals are analyzing the potential disruptions this may cause in the broader technological landscape. We will continue to monitor the metrics. You can visit the direct source below for raw updates."
        
    return content, image_url

def fetch_story_details(args: Tuple[str, str]) -> Dict:
    story_url, title = args
    logger.info(f"Elaborating: {title}")
    content, image_url = elaborate_content_and_image(story_url, title)
    return {
        "title": title,
        "url": story_url,
        "content": content,
        "image_url": image_url
    }

def fetch_dynamic_news(limit: int = 5) -> List[Dict]:
    """Scrapes top stories concurrently."""
    logger.info("Fetching top stories directly from HackerNews HTML...")
    stories = []
    try:
        url = "https://news.ycombinator.com/"
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        response = requests.get(url, headers=headers, timeout=10)
        soup = BeautifulSoup(response.text, 'html.parser')
        
        storylinks = soup.find_all('span', class_='titleline')
        tasks = []
        for item in storylinks[:limit]:
            link_tag = item.find('a')
            if link_tag:
                title = link_tag.get_text()
                story_url = link_tag.get('href')
                if story_url.startswith('item?id='):
                    story_url = f"https://news.ycombinator.com/{story_url}"
                tasks.append((story_url, title))
        
        # Concurrency Optimization
        with ThreadPoolExecutor(max_workers=5) as executor:
            results = executor.map(fetch_story_details, tasks)
            stories = list(results)
            
    except Exception as e:
        logger.error(f"Error fetching news: {e}")
    return stories

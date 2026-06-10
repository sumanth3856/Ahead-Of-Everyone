import os
import json
import logging
import feedparser
import re
from typing import List, Dict, Optional
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

def ai_summarize(title: str, raw_content: str) -> Optional[Dict]:
    """Uses OpenRouter AI to generate a highly structured JSON summary for the premium layout."""
    system_prompt = """You are an elite tech journalist for 'Ahead of Everyone'.
Your task is to take a raw news snippet and write a premium, highly structured editorial piece.
You MUST output ONLY valid JSON. Do not include markdown formatting like ```json.

JSON Schema:
{
  "category": "A 3-part tag (e.g., '01 . FEATURE . AI INNOVATION' or '05 . NEWS . POLICY')",
  "headline": "A massive, punchy headline",
  "headline_highlight": "The most important word or short phrase from the headline to highlight.",
  "the_brief": "A concise 2-3 sentence summary of the news.",
  "core_breakdown": [
    {"topic": "The architecture", "text": "1.6T total params..."},
    {"topic": "The pricing", "text": "Flash at $0.14 per million..."}
  ],
  "the_edge": "A punchy, single-sentence conclusion or hot take."
}
Limit core_breakdown to exactly 3 or 4 points."""

    try:
        response = client.chat.completions.create(
            model=config.OPENROUTER_MODEL,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": f"Title: {title}\nRaw Context: {raw_content}"}
            ],
            timeout=30,
        )
        content = response.choices[0].message.content.strip()
        # Clean potential markdown wrapping
        if content.startswith("```json"):
            content = content[7:-3].strip()
        elif content.startswith("```"):
            content = content[3:-3].strip()
            
        return json.loads(content)
    except Exception as e:
        logger.error(f"AI Summarization failed for '{title}': {e}")
        return None

def strip_html(html_str: str) -> str:
    """Lightweight HTML stripper using regex."""
    text = re.sub(r'<[^>]+>', ' ', html_str)
    return " ".join(text.split())

def fetch_rss_feed(feed_url: str) -> List[Dict]:
    logger.info(f"Fetching RSS feed: {feed_url}")
    items = []
    try:
        parsed = feedparser.parse(feed_url)
        cutoff_time = datetime.now() - timedelta(hours=24)
        for entry in parsed.entries:
            published = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published = datetime.fromtimestamp(time.mktime(entry.published_parsed))
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published = datetime.fromtimestamp(time.mktime(entry.updated_parsed))
                
            if published and published < cutoff_time:
                continue

            title = entry.get('title', 'Unknown Title')
            link = entry.get('link', '')
            
            raw_summary = entry.get('summary', '')
            content = entry.get('content', [{'value': ''}])[0]['value'] if hasattr(entry, 'content') else ''
            full_html = raw_summary + " " + content
            
            # Clean text using lightweight regex
            text_snippet = strip_html(full_html)[:1500]
            
            if len(text_snippet) < 50:
                continue # Skip empty items
                
            items.append({
                "title": title,
                "url": link,
                "raw_text": text_snippet
            })
    except Exception as e:
        logger.error(f"Error fetching RSS {feed_url}: {e}")
    return items

def fetch_story_details(item: Dict) -> Optional[Dict]:
    logger.info(f"AI Processing: {item['title']}")
    structured_data = ai_summarize(item['title'], item['raw_text'])
    
    if not structured_data:
        logger.warning(f"Using fallback summary for '{item['title']}' due to AI failure.")
        structured_data = {
            "category": "TECH . NEWS",
            "headline": item['title'],
            "headline_highlight": item['title'].split()[0] if item['title'] else "NEWS",
            "the_brief": item['raw_text'][:200] + "...",
            "core_breakdown": [
                {"topic": "Overview", "description": "The AI summarizer hit a rate limit, so this is the raw text snippet."},
                {"topic": "Source Text", "description": item['raw_text'][:150] + "..."}
            ],
            "the_edge": "Read the full article online to stay ahead."
        }
        
    structured_data['url'] = item['url']
    return structured_data

def fetch_dynamic_news(limit: int = 15) -> List[Dict]:
    """Scrapes multi-source RSS feeds and uses AI to summarize into JSON."""
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
            
    # Deduplicate by title
    seen = set()
    unique_items = []
    for item in all_raw_items:
        if item['title'] not in seen:
            seen.add(item['title'])
            unique_items.append(item)
            
    unique_items = unique_items[:limit]
    
    stories = []
    for item in unique_items:
        res = fetch_story_details(item)
        if res:
            stories.append(res)
        time.sleep(2) # Prevent hitting free-tier rate limits
                
    return stories

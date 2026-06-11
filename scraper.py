import os
import json
import logging
import feedparser
import re
from typing import List, Dict, Optional
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
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
        max_retries=0,
    )

client = init_openai_client()

REGISTRY_FILE = "sent_articles.json"
REGISTRY_RETENTION_DAYS = 7

def load_sent_registry() -> List[Dict]:
    if os.path.exists(REGISTRY_FILE):
        try:
            with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            logger.error(f"Error loading registry: {e}")
    return []

def save_sent_registry(registry: List[Dict]) -> None:
    try:
        with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
            json.dump(registry, f, indent=2, ensure_ascii=False)
    except Exception as e:
        logger.error(f"Error saving registry: {e}")

def prune_registry(registry: List[Dict]) -> List[Dict]:
    cutoff = datetime.now(timezone.utc) - timedelta(days=REGISTRY_RETENTION_DAYS)
    pruned = []
    for item in registry:
        try:
            item_time = datetime.fromisoformat(item['timestamp'].replace("Z", "+00:00"))
            if item_time.tzinfo is None:
                item_time = item_time.replace(tzinfo=timezone.utc)
            if item_time >= cutoff:
                pruned.append(item)
        except Exception as e:
            pruned.append(item)
    return pruned

def is_duplicate_or_rehash(title: str, url: str, registry: List[Dict]) -> bool:
    if any(item['url'] == url for item in registry):
        return True
    
    clean_title = title.lower().strip()
    if any(item['title'].lower().strip() == clean_title for item in registry):
        return True
        
    words_new = set(re.findall(r'\w+', clean_title))
    if not words_new:
        return False
        
    for item in registry:
        words_old = set(re.findall(r'\w+', item['title'].lower().strip()))
        intersection = words_new.intersection(words_old)
        union = words_new.union(words_old)
        if union:
            jaccard = len(intersection) / len(union)
            if jaccard > 0.7:
                update_keywords = ['update', 'updated', 'live', 'developing', 'latest', 'detailed', 'new details', 'clarification']
                if any(kw in clean_title for kw in update_keywords):
                    logger.info(f"Allowing update/developing article: {title}")
                    return False
                logger.info(f"Filtered out similar/duplicate article: '{title}' (matches '{item['title']}' with Jaccard {jaccard:.2f})")
                return True
    return False

def register_sent_stories(stories: List[Dict]) -> None:
    registry = load_sent_registry()
    now_str = datetime.now(timezone.utc).isoformat()
    for story in stories:
        registry.append({
            "url": story.get("url", ""),
            "title": story.get("headline", ""),
            "timestamp": now_str
        })
    registry = prune_registry(registry)
    save_sent_registry(registry)
    logger.info(f"Registered {len(stories)} articles in registry and pruned old entries.")

def ai_summarize(title: str, raw_content: str) -> Optional[Dict]:
    """Uses OpenRouter AI to generate a highly structured JSON summary for the premium layout."""
    system_prompt = """You are an elite tech journalist for 'Ahead of Everyone'.
Your task is to take a raw news snippet and write a premium, highly structured editorial piece.
You MUST output ONLY valid JSON. Do not include markdown formatting like ```json.

JSON Schema:
{
  "category": "A 3-part tag (e.g., '01 . FEATURE . AI INNOVATION' or '05 . NEWS . POLICY')",
  "headline": "An eye-catching, scroll-stopping, and attention-grabbing headline that rephrases the original to hook the reader (avoid dry or boring titles)",
  "headline_highlight": "The most important, high-impact word or short phrase from the rewritten headline to highlight.",
  "the_brief": "A highly concise 1-2 sentence summary of the news (maximum 160 characters).",
  "core_breakdown": [
    {
      "topic": "1-2 word category/topic (e.g., 'Market impact' or 'Tech shift')",
      "description": "A concise detail (maximum 90 characters)"
    },
    {
      "topic": "1-2 word category/topic",
      "description": "A concise detail (maximum 90 characters)"
    }
  ],
  "the_edge": "A punchy, single-sentence future-looking takeaway or hot take (maximum 100 characters)."
}"""

    FALLBACK_MODELS = [
        config.OPENROUTER_MODEL,
        "openrouter/free",
        "meta-llama/llama-3.1-8b-instruct:free",
        "nvidia/nemotron-3-ultra-550b-a55b:free"
    ]

    for model_id in FALLBACK_MODELS:
        try:
            response = client.chat.completions.create(
                model=model_id,
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Title: {title}\nRaw Context: {raw_content}"}
                ],
                timeout=12,
            )
            content = response.choices[0].message.content.strip()
            # Clean potential markdown wrapping
            if content.startswith("```json"):
                content = content[7:-3].strip()
            elif content.startswith("```"):
                content = content[3:-3].strip()
                
            return json.loads(content)
        except Exception as e:
            logger.warning(f"Model {model_id} failed for '{title}': {e}. Attempting next model...")
            continue
            
    logger.error(f"All AI models exhausted for '{title}'.")
    return None

def strip_html(html_str: str) -> str:
    """Lightweight HTML stripper using regex."""
    text = re.sub(r'<[^>]+>', ' ', html_str)
    return " ".join(text.split())

def fetch_rss_feed(feed_url: str, lookback_hours: int = 24) -> List[Dict]:
    logger.info(f"Fetching RSS feed: {feed_url} with {lookback_hours}h lookback")
    items = []
    try:
        parsed = feedparser.parse(feed_url)
        cutoff_time = datetime.now() - timedelta(hours=lookback_hours)
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
            content = ""
            if hasattr(entry, 'content') and entry.content:
                content = entry.content[0].get('value', '')
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
        
        # Clean title by removing source suffix (e.g., " - TechCrunch")
        clean_headline = re.sub(r'\s+[-|]\s+[^|-]+$', '', item['title']).strip()
        highlight = clean_headline.split()[0] if clean_headline else "NEWS"
        
        # Clean and extract first 1-2 sentences of raw text up to 160 chars
        snippet = item['raw_text'].strip()
        sentences = re.split(r'(?<=[.!?])\s+', snippet)
        brief = ""
        for s in sentences:
            if len(brief) + len(s) + 1 <= 160:
                brief += (s + " ")
            else:
                break
        brief = brief.strip()
        if not brief:
            brief = snippet[:157] + "..."
            
        # Dynamically guess category based on title keywords or feed source
        lower_title = clean_headline.lower()
        if "ai" in lower_title or "artificial intelligence" in lower_title or "model" in lower_title:
            category = "02 . FEATURE . AI & RESEARCH"
        elif "cyber" in lower_title or "hack" in lower_title or "security" in lower_title or "vulnerability" in lower_title:
            category = "03 . ALERT . CYBERSECURITY"
        elif "policy" in lower_title or "court" in lower_title or "ban" in lower_title or "regulation" in lower_title:
            category = "04 . NEWS . REGULATION"
        else:
            category = "05 . NEWS . TECH POLICY"

        structured_data = {
            "category": category,
            "headline": clean_headline,
            "headline_highlight": highlight,
            "the_brief": brief,
            "core_breakdown": [
                {"topic": "Context", "description": "Rapidly developing story. Full intelligence synthesis is currently compiling."},
                {"topic": "Update", "description": "Please review the source link for raw, unfiltered developments."}
            ],
            "the_edge": "A critical industry update to watch as developments unfold."
        }
        
    structured_data['url'] = item['url']
    return structured_data

def fetch_dynamic_news(limit: int = 7) -> List[Dict]:
    """Scrapes multi-source RSS feeds, filters duplicates/rehashes, and uses AI to summarize 5-7 stories."""
    logger.info("Fetching multi-source RSS feeds...")
    rss_feeds = [
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml",
        "https://www.wired.com/feed/rss",
        "https://news.ycombinator.com/rss"
    ]
    
    registry = load_sent_registry()
    unique_candidates = []
    chosen_lookback = 24
    
    # Try lookbacks of 24h, 48h, 72h to ensure at least 5 articles
    for lookback in [24, 48, 72]:
        chosen_lookback = lookback
        all_raw_items = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            # Pass lookback parameter using lambda to avoid issues
            results = executor.map(lambda url: fetch_rss_feed(url, lookback), rss_feeds)
            for res in results:
                all_raw_items.extend(res)
                
        # Group raw items by feed URL to enable interleaving later
        feed_grouped = {url: [] for url in rss_feeds}
        seen_titles = set()
        
        for item in all_raw_items:
            if item['title'] in seen_titles:
                continue
            if is_duplicate_or_rehash(item['title'], item['url'], registry):
                continue
                
            seen_titles.add(item['title'])
            
            # Map item back to its feed source
            matched_feed = rss_feeds[0]
            for url in rss_feeds:
                domain = url.split("//")[-1].split("/")[0]
                if domain in item['url']:
                    matched_feed = url
                    break
            feed_grouped[matched_feed].append(item)
            
        # Interleave items from different feeds for source diversity
        interleaved = []
        max_len = max(len(feed_grouped[url]) for url in rss_feeds) if feed_grouped else 0
        for i in range(max_len):
            for url in rss_feeds:
                if i < len(feed_grouped[url]):
                    interleaved.append(feed_grouped[url][i])
                    
        unique_candidates = interleaved
        logger.info(f"Lookback {lookback}h: found {len(unique_candidates)} non-sent unique candidates")
        
        if len(unique_candidates) >= 5:
            break
            
    logger.info(f"Final selected lookback: {chosen_lookback}h with {len(unique_candidates)} candidates")
    
    # Enforce story limits: strictly 5 stories
    target_limit = 5
    selected_items = unique_candidates[:target_limit]
    logger.info(f"Selected {len(selected_items)} stories for AI processing.")
    
    stories = []
    for item in selected_items:
        res = fetch_story_details(item)
        if res:
            stories.append(res)
        time.sleep(4) # Prevent hitting free-tier rate limits
        
    return stories

def fetch_targeted_news(query: str, limit: int = 5) -> List[Dict]:
    """Scrapes Google News RSS for a specific topic, bypassing the anti-rehash registry."""
    logger.info(f"Fetching targeted news for query: {query}")
    
    # URL encode query
    encoded_query = query.replace(" ", "%20")
    rss_feed = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    raw_items = fetch_rss_feed(rss_feed, lookback_hours=72)
    
    # Deduplicate by title
    seen = set()
    unique_items = []
    for item in raw_items:
        if item['title'] not in seen:
            seen.add(item['title'])
            unique_items.append(item)
            
    selected_items = unique_items[:limit]
    logger.info(f"Selected {len(selected_items)} targeted stories for AI processing.")
    
    stories = []
    for item in selected_items:
        res = fetch_story_details(item)
        if res:
            stories.append(res)
        time.sleep(4)
        
    return stories

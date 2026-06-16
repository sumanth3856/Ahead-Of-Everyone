import os
import json
import logging
import feedparser
import re
import aiohttp
import asyncio
from typing import List, Dict, Optional
from datetime import datetime, timedelta, timezone
import time
import calendar
import urllib.parse
from openai import AsyncOpenAI
from dotenv import load_dotenv
from bs4 import BeautifulSoup
import json_repair

import config
from database import get_http_session

logger = logging.getLogger(__name__)
load_dotenv()

OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")

def init_openai_client():
    if not OPENROUTER_API_KEY:
        logger.warning("OPENROUTER_API_KEY is not set. AI Summarization will fail.")
    return AsyncOpenAI(
        base_url=config.OPENROUTER_API_URL,
        api_key=OPENROUTER_API_KEY or "dummy_key_to_prevent_startup_crash",
        max_retries=0,
    )

client = init_openai_client()

REGISTRY_FILE = "sent_articles.json"
REGISTRY_RETENTION_DAYS = 7

# Pre-compiled regex patterns for high-performance string operations
HTML_STRIP_RE = re.compile(r'<[^>]+>')
WORD_TOKEN_RE = re.compile(r'\w+')
HEADLINE_CLEAN_RE = re.compile(r'\s+[-|]\s+[^|-]+$')



async def load_sent_registry() -> List[Dict]:
    def _load():
        if os.path.exists(REGISTRY_FILE):
            try:
                with open(REGISTRY_FILE, "r", encoding="utf-8") as f:
                    return json.load(f)
            except (json.JSONDecodeError, IOError) as e:
                logger.error(f"Error loading registry, backing up corrupted file: {e}")
                try:
                    corrupted_backup = f"{REGISTRY_FILE}.corrupted.{int(time.time())}"
                    os.rename(REGISTRY_FILE, corrupted_backup)
                    logger.info(f"Renamed corrupted registry file to {corrupted_backup}")
                except Exception as backup_err:
                    logger.error(f"Could not rename corrupted registry: {backup_err}")
        return []
    return await asyncio.to_thread(_load)

async def save_sent_registry(registry: List[Dict]) -> None:
    def _save():
        try:
            with open(REGISTRY_FILE, "w", encoding="utf-8") as f:
                json.dump(registry, f, indent=2, ensure_ascii=False)
        except Exception as e:
            logger.error(f"Error saving registry: {e}")
    await asyncio.to_thread(_save)

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
            logger.warning(f"Dropping corrupt registry item during prune: {e}")
    return pruned

def is_duplicate_or_rehash(title: str, url: str, registry: List[Dict], jaccard_threshold: float = 0.7) -> bool:
    if any(item.get('url') == url for item in registry):
        return True
    
    clean_title = title.lower().strip()
    if any(item.get('title', '').lower().strip() == clean_title for item in registry):
        return True
        
    words_new = set(WORD_TOKEN_RE.findall(clean_title))
    if not words_new:
        return False
        
    for item in registry:
        # Optimization: Use precomputed token set if available to avoid O(M*N) regex executions
        if 'token_set' not in item:
            item['token_set'] = set(WORD_TOKEN_RE.findall(item.get('title', '').lower().strip()))
        words_old = item['token_set']
        
        intersection = words_new.intersection(words_old)
        union = words_new.union(words_old)
        if union:
            jaccard = len(intersection) / len(union)
            if jaccard > jaccard_threshold:
                update_keywords = ['update', 'updated', 'live', 'developing', 'latest', 'detailed', 'new details', 'clarification']
                if any(kw in clean_title for kw in update_keywords):
                    logger.info(f"Allowing update/developing article: {title}")
                    return False
                logger.info(f"Filtered out similar/duplicate article: '{title}' (matches '{item.get('title', '')}' with Jaccard {jaccard:.2f})")
                return True
    return False

async def register_sent_stories(stories: List[Dict]) -> None:
    registry = await load_sent_registry()
    now_str = datetime.now(timezone.utc).isoformat()
    for story in stories:
        registry.append({
            "url": story.get("url", ""),
            "title": story.get("original_title", story.get("headline", "")),
            "timestamp": now_str
        })
    registry = prune_registry(registry)
    await save_sent_registry(registry)
    logger.info(f"Registered {len(stories)} articles in registry and pruned old entries.")

def clean_json_content(content: str) -> str:
    content = content.strip()
    if content.startswith("```json"):
        content = content[7:]
    elif content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()
    return content

def clean_markdown_text(text) -> str:
    if not isinstance(text, str):
        return text
    # Remove literal markdown bold asterisks and underscores
    text = text.replace("**", "").replace("__", "")
    text = text.strip()
    # Remove literal explicit quotes if the AI accidentally added them inside the string value
    if text.startswith('"') and text.endswith('"') and len(text) > 1:
        text = text[1:-1]
    if text.startswith("'") and text.endswith("'") and len(text) > 1:
        text = text[1:-1]
    return text.strip()

def try_parse_json(content: str) -> Optional[Dict]:
    content = clean_json_content(content)
    parsed = None
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        try:
            logger.info("Attempting local algorithmic JSON repair...")
            parsed = json_repair.repair_json(content, return_objects=True)
        except Exception as e:
            logger.warning(f"Local JSON repair failed: {e}")
                
    if parsed and isinstance(parsed, dict):
        for k, v in parsed.items():
            if isinstance(v, str):
                parsed[k] = clean_markdown_text(v)
        return parsed
        
    return None

async def _execute_llm_completion(model_id: str, system_prompt: str, user_msg: str, timeout: int = 60) -> Optional[str]:
    """Helper function to execute OpenRouter/OpenAPI completion call."""
    try:
        response = await client.chat.completions.create(
            model=model_id,
            messages=[{"role": "system", "content": system_prompt}, {"role": "user", "content": user_msg}],
            timeout=timeout,
        )
        if hasattr(response, 'choices') and response.choices:
            return response.choices[0].message.content.strip()
    except Exception as e:
        logger.warning(f"[AI] API call failed for model {model_id}: {e}")
    return None

async def ai_summarize(title: str, raw_content: str, metadata: Optional[Dict] = None) -> Optional[Dict]:
    """Uses OpenRouter AI to generate a highly structured JSON summary for the premium layout."""
    system_prompt = """You are an elite, Pulitzer-winning tech journalist for 'Ahead of Everyone'.
Your job is to read raw, noisy article content and perform a DEEP SUMMARIZATION.
You must distill the content down to 80% compression—meaning you preserve the full factual picture, critical details, nuance, and context, while removing the bloat. 
DO NOT hallucinate. DO NOT copy-paste directly. Write entirely original, engaging journalistic prose.
IGNORE website navigation menus, cookie banners, headers, and irrelevant noise.

You MUST output ONLY valid JSON matching this exact schema, with no markdown formatting around it:
{
  "category": "String (Generate a 2-4 word topic category, e.g., 'FEATURE . AI', 'ALERT . CYBERSECURITY', 'SPORT . CRICKET', 'NEWS . POLICY')",
  "headline": "Cleaned, punchy version of the article title",
  "headline_highlight": "One single powerful word representing the headline",
  "the_brief": "A 1-2 sentence executive summary of what happened.",
  "core_breakdown": [
    {
      "tag": "String: Short, 1-3 word bold lead-in descriptor (e.g., 'The deal', 'The architecture', 'The pricing')",
      "detail": "String: The punchy factual details and metrics for this point (~150-250 characters)"
    }
  ],
  "the_edge": "The critical take, market impact, or 'why this matters' (~350 chars).",
  "deep_dive": "An insightful quote from the article or final piece of critical context (~300 chars)."
}
Note: The 'core_breakdown' list MUST contain exactly 4 key objects covering the core facts of the story."""

    # Build user message with social context if available
    user_msg = f"Title: {title}\nRaw Context: {raw_content}"
    if metadata:
        context_parts = []
        if metadata.get('source'): context_parts.append(f"Source: {metadata['source']}")
        if metadata.get('upvotes'): context_parts.append(f"Community Engagement: {metadata['upvotes']} upvotes")
        if metadata.get('sector'): context_parts.append(f"Sector Hint: {metadata['sector']}")
        if context_parts: user_msg += "\n\nSocial Context: " + ", ".join(context_parts)

    primary_model = config.OPENROUTER_MODEL
    backup_models = [
        "openai/gpt-oss-120b:free",              # Fallback 1: OpenAI-quality JSON, 131K context
        "meta-llama/llama-3.3-70b-instruct:free", # Fallback 2: Battle-tested, highly stable
        "google/gemma-4-31b-it:free",            # Fallback 3: Google-backed, 262K context
        "openrouter/free",                       # Last Resort: Meta-router
    ]

    # 1. Primary Model Attempt
    logger.info(f"[AI] Processing: {title} (Model: {primary_model})")
    content = await _execute_llm_completion(primary_model, system_prompt, user_msg)
    if content:
        parsed = try_parse_json(content)
        if parsed:
            logger.info(f"[AI] Successfully processed: {title} (Model: {primary_model})")
            return parsed

    # 2. Sequential Backup Model Attempts
    logger.info(f"Primary model failed. Falling back to {len(backup_models)} backup models sequentially for '{title}'...")
    
    for model_id in backup_models:
        logger.info(f"[AI] Processing fallback: {title} (Model: {model_id})")
        content = await _execute_llm_completion(model_id, system_prompt, user_msg)
        if content:
            parsed = try_parse_json(content)
            if parsed:
                logger.info(f"[AI] Successfully processed: {title} (Model: {model_id})")
                return parsed
            
    logger.error(f"All AI models exhausted for '{title}'.")
    return None

def strip_html(html_str: str) -> str:
    """Lightweight HTML stripper using pre-compiled regex."""
    text = HTML_STRIP_RE.sub(' ', html_str)
    return " ".join(text.split())

async def fetch_rss_feed(feed_url: str, lookback_hours: int = 24) -> List[Dict]:
    logger.info(f"[SCRAPER] Fetching RSS feed: {feed_url} with {lookback_hours}h lookback")
    items = []
    try:
        # Pass custom User-Agent to prevent 403 Forbidden errors
        agent = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
        session = await get_http_session()
        async with session.get(feed_url, headers={"User-Agent": agent}, timeout=15) as resp:
            content = await resp.text()
            
        # Parse XML concurrently to avoid blocking event loop
        parsed = await asyncio.to_thread(feedparser.parse, content)
        
        cutoff_time = datetime.now(timezone.utc) - timedelta(hours=lookback_hours)
        for entry in parsed.entries:
            published = None
            if hasattr(entry, 'published_parsed') and entry.published_parsed:
                published = datetime.fromtimestamp(calendar.timegm(entry.published_parsed), timezone.utc)
            elif hasattr(entry, 'updated_parsed') and entry.updated_parsed:
                published = datetime.fromtimestamp(calendar.timegm(entry.updated_parsed), timezone.utc)
                
            if published and published < cutoff_time:
                continue

            title = entry.get('title', 'Unknown Title')
            link = entry.get('link', '')
            
            raw_summary = entry.get('summary', '')
            content_val = ""
            if hasattr(entry, 'content') and entry.content:
                content_val = entry.content[0].get('value', '')
            full_html = raw_summary + " " + content_val
            
            # Clean text using lightweight regex
            text_snippet = strip_html(full_html)[:1500]
            
            if len(text_snippet) < 50:
                continue # Skip empty items
                
            items.append({
                "title": title,
                "url": link,
                "raw_text": text_snippet,
                "published": published
            })
    except Exception as e:
        logger.error(f"Error fetching RSS {feed_url}: {e}")
    return items

def is_block_or_error_page(text: str) -> bool:
    if not text:
        return False
    lower_text = text.lower()
    signatures = [
        "429 too many requests",
        "too many requests",
        "access denied",
        "cloudflare",
        "security check",
        "bot protection",
        "403 forbidden",
        "unauthorized",
        "hcaptcha",
        "recaptcha"
    ]
    for sig in signatures:
        if sig in lower_text:
            return True
    return False

async def fetch_full_article_text(url: str) -> str:
    """Scrapes the full article text from the URL using Jina Reader (with BeautifulSoup fallback)."""
    logger.info(f"Attempting deep scrape for text using Jina Reader: {url}")
    session = await get_http_session()
    
    # Attempt 1: Jina Reader API (bypass JS/Bot protections)
    try:
        jina_url = f"https://r.jina.ai/{url}"
        async with session.get(
            jina_url,
            headers={
                "Accept": "text/plain",
                "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
            },
            timeout=15
        ) as resp:
            resp.raise_for_status()
            text = await resp.text()
            if is_block_or_error_page(text):
                logger.warning(f"Jina Reader returned a block/error signature page for {url}")
            elif len(text.strip()) > 50:
                logger.info(f"Successfully scraped with Jina Reader: {url}")
                return text
    except Exception as e:
        logger.info(f"Jina Reader scrape failed for {url}: {e}. Falling back to standard scrape.")

    # Attempt 2: Standard BeautifulSoup Fallback
    try:
        async with session.get(
            url,
            headers={"User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"},
            timeout=10
        ) as resp:
            resp.raise_for_status()
            text_content = await resp.text()
            if is_block_or_error_page(text_content):
                logger.warning(f"Standard fallback returned a block/error signature page for {url}")
                return ""
            
        def parse_html(html):
            soup = BeautifulSoup(html, 'html.parser')
            for script in soup(["script", "style", "nav", "footer", "header", "aside"]):
                script.extract()
            paragraphs = soup.find_all('p')
            return " ".join([p.get_text().strip() for p in paragraphs if p.get_text().strip()])
            
        text = await asyncio.to_thread(parse_html, text_content)
        if len(text.strip()) > 50:
             logger.info(f"Successfully scraped with standard fallback: {url}")
        return text
    except Exception as e:
        logger.warning(f"Fallback scrape also failed for {url}: {e}")
        return ""

async def fetch_story_details(item: Dict) -> Optional[Dict]:
    logger.info(f"[SCRAPER] Starting AI Processing for: {item['title']}")
    metadata = item.get('metadata', None)
    
    # 1. Fetch full text FIRST using Jina Reader (check cache first)
    full_text_raw = item.get('scraped_full_text', None)
    if not full_text_raw:
        full_text_raw = await fetch_full_article_text(item['url'])
    
    # 2. Clean the markdown noise to save tokens & improve accuracy
    import re
    cleaned_text = full_text_raw
    if cleaned_text:
        # Remove markdown image links ![...](...)
        cleaned_text = re.sub(r'!\[.*?\]\(.*?\)', '', cleaned_text)
        # Remove markdown links but keep text: [text](url) -> text
        cleaned_text = re.sub(r'\[([^\]]+)\]\([^)]+\)', r'\1', cleaned_text)
        # Collapse multiple spaces/newlines
        cleaned_text = re.sub(r'\s+', ' ', cleaned_text).strip()
        # Truncate to a reasonable length (e.g. 15000 chars)
        cleaned_text = cleaned_text[:15000]
    
    if not cleaned_text or len(cleaned_text) < 100:
        logger.info(f"[SCRAPER] Full text extraction failed or too short, falling back to RSS snippet for: {item['url']}")
        cleaned_text = item['raw_text']
        
    logger.info(f"[SCRAPER] Cleaned text ready ({len(cleaned_text)} chars). Sending to AI model...")
    
    # 3. AI Summarization
    structured_data = await ai_summarize(item['title'], cleaned_text, metadata=metadata)
    full_text = cleaned_text  # Make available for fallback logic
    
    # Clean headline & highlight for fallbacks
    clean_headline = HEADLINE_CLEAN_RE.sub('', item['title']).strip()
    highlight = clean_headline.split()[0] if clean_headline else "NEWS"
    
    def fallback_assign(structured_data, key, text_source, limit, default_msg):
        if is_empty_value(structured_data.get(key)):
            if text_source:
                text = " ".join(text_source.split())
                if len(text) > limit:
                    slice_limit = limit - 3
                    sub_text = text[:slice_limit]
                    last_space = sub_text.rfind(' ')
                    if last_space != -1:
                        text = sub_text[:last_space].rstrip(".,;:!- ") + "..."
                    else:
                        text = sub_text + "..."
                structured_data[key] = text
            else:
                structured_data[key] = default_msg
        else:
            val_str = " ".join(str(structured_data[key]).strip().strip('\'"').split())
            if len(val_str) > limit:
                slice_limit = limit - 3
                sub_text = val_str[:slice_limit]
                last_space = sub_text.rfind(' ')
                if last_space != -1:
                    val_str = sub_text[:last_space].rstrip(".,;:!- ") + "..."
                else:
                    val_str = sub_text + "..."
            structured_data[key] = val_str

    def is_empty_value(val) -> bool:
        if val is None:
            return True
        s = str(val).strip()
        # Checks for empty string, quotes, or whitespace
        return not s or s in ('""', "''", '""""', "''''", '`""`', "`''`")

    if not structured_data:
        logger.warning(f"Using fallback summary for '{item['title']}' due to AI failure.")
        structured_data = {}

    # Category fallback
    if is_empty_value(structured_data.get("category")):
        sector = (metadata or {}).get('sector', '')
        lower_title = clean_headline.lower()
        if sector == 'science':
            structured_data["category"] = "03 . SECTOR . SCIENCE"
        elif sector == 'medical':
            structured_data["category"] = "04 . SECTOR . MEDICAL & PHARMA"
        elif sector == 'agriculture':
            structured_data["category"] = "05 . SECTOR . AGRICULTURE"
        elif sector == 'weather':
            structured_data["category"] = "05 . SECTOR . CLIMATE & WEATHER"
        elif "ai" in lower_title or "artificial intelligence" in lower_title or "model" in lower_title:
            structured_data["category"] = "02 . FEATURE . AI & RESEARCH"
        elif "cyber" in lower_title or "hack" in lower_title or "security" in lower_title or "vulnerability" in lower_title:
            structured_data["category"] = "03 . ALERT . CYBERSECURITY"
        elif "policy" in lower_title or "court" in lower_title or "ban" in lower_title or "regulation" in lower_title:
            structured_data["category"] = "04 . NEWS . REGULATION"
        else:
            structured_data["category"] = "05 . NEWS . TECH POLICY"
    else:
        # Strip outer quotes if any
        structured_data["category"] = str(structured_data["category"]).strip().strip('\'"')

    # Headline fallback
    if is_empty_value(structured_data.get("headline")):
        structured_data["headline"] = clean_headline
    else:
        structured_data["headline"] = str(structured_data["headline"]).strip().strip('\'"')

    # Headline Highlight fallback
    if is_empty_value(structured_data.get("headline_highlight")):
        structured_data["headline_highlight"] = highlight
    else:
        structured_data["headline_highlight"] = str(structured_data["headline_highlight"]).strip().strip('\'"')

    # The Brief fallback
    if is_empty_value(structured_data.get("the_brief")):
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
        structured_data["the_brief"] = brief
    else:
        structured_data["the_brief"] = str(structured_data["the_brief"]).strip().strip('\'"')

    # Core Breakdown fallback (Must be a list of exactly 4 objects with tag and detail keys)
    raw_core = structured_data.get("core_breakdown")
    is_valid_list = isinstance(raw_core, list) and len(raw_core) > 0 and all(isinstance(x, dict) and "tag" in x and "detail" in x for x in raw_core)
    
    if not is_valid_list:
        if isinstance(raw_core, str) and raw_core.strip():
            fallback_text = raw_core
        else:
            if full_text and len(full_text) > 100:
                snippet = full_text
            brief = structured_data["the_brief"]
            remaining_text = snippet[len(brief):].strip() if snippet.startswith(brief) else snippet
            if not remaining_text:
                remaining_text = "Rapidly developing story. Full intelligence synthesis is currently compiling. Please review the source link for raw, unfiltered developments."
            fallback_text = remaining_text
            
        # Split fallback_text into sentences
        sentences = [s.strip() for s in re.split(r'(?<=[.!?])\s+', fallback_text) if s.strip()]
        while len(sentences) < 4:
            sentences.append("Additional context and verification is being compiled by our intelligence desk.")
        if len(sentences) > 4:
            sentences[3] = " ".join(sentences[3:])
            sentences = sentences[:4]
            
        tags = ["The update", "The details", "The impact", "The outlook"]
        structured_data["core_breakdown"] = [
            {"tag": tags[i], "detail": sentences[i][:250]} for i in range(4)
        ]
    else:
        cleaned_list = []
        for i in range(4):
            if i < len(raw_core):
                c_item = raw_core[i]
                tag = str(c_item.get("tag", "The detail")).strip().strip('\'"')
                detail = str(c_item.get("detail", "Additional context under review.")).strip().strip('\'"')
                cleaned_list.append({"tag": tag, "detail": detail})
            else:
                cleaned_list.append({
                    "tag": "The outlook",
                    "detail": "Additional validation and research continues as the story develops."
                })
        structured_data["core_breakdown"] = cleaned_list

    # Compute remaining text for The Edge and Deep Dive
    if not full_text or len(full_text) < 100:
        full_text = item['raw_text']
        
    brief = structured_data.get("the_brief", "")
    core_texts = [x.get("detail", "") for x in structured_data.get("core_breakdown", [])]
    core = " ".join(core_texts).replace("...", "")
    
    # Try to find where core ends
    idx = full_text.find(core)
    if idx != -1:
        leftover_text = full_text[idx + len(core):].strip()
    else:
        leftover_text = full_text[len(brief) + len(core):].strip()

    # The Edge fallback
    # The Edge fallback
    fallback_assign(structured_data, "the_edge", leftover_text, 350, "A critical industry update to watch as developments unfold.")

    # Update leftover_text for Deep Dive
    edge_str = structured_data.get("the_edge", "").replace("...", "")
    idx = leftover_text.find(edge_str)
    if idx != -1:
        deep_leftover = leftover_text[idx + len(edge_str):].strip()
    else:
        deep_leftover = leftover_text[len(edge_str):].strip()

    # The Deep Dive fallback
    # The Deep Dive fallback
    fallback_assign(structured_data, "deep_dive", deep_leftover, 800, "Continue tracking this story for deeper implications.")
        
    structured_data['url'] = item['url']
    structured_data['original_title'] = item['title']
    return structured_data

# ─── Hacker News Firebase API ───────────────────────────────────────────────

HN_USER_AGENT = "AoE-Bot/2.0 (Ahead of Everyone Daily Digest)"

async def fetch_hn_top_stories(limit: int = 10) -> List[Dict]:
    """Fetches top stories from Hacker News concurrently."""
    logger.info(f"[SCRAPER] Fetching top {limit} stories from Hacker News API...")
    try:
        session = await get_http_session()
        async with session.get(
            "https://hacker-news.firebaseio.com/v0/topstories.json",
            headers={"User-Agent": HN_USER_AGENT},
            timeout=10
        ) as resp:
            resp.raise_for_status()
            story_ids = await resp.json()
            story_ids = story_ids[:limit * 3]
    except Exception as e:
        logger.error(f"[SCRAPER] Error fetching HN top story IDs: {e}")
        return []

    items = []
    
    async def fetch_single_story(sid):
        try:
            async with session.get(
                f"https://hacker-news.firebaseio.com/v0/item/{sid}.json",
                headers={"User-Agent": HN_USER_AGENT},
                timeout=8
            ) as detail_resp:
                detail = await detail_resp.json()
                
            if not detail or detail.get('type') != 'story' or not detail.get('url'):
                return None

            title = detail.get('title', '')
            url = detail.get('url', '')
            score = detail.get('score', 0)
            comments = detail.get('descendants', 0)
            text = detail.get('text', '') or ''
            raw_text = strip_html(text) if text else title
            if len(raw_text) < 50:
                raw_text = f"{title}. This article has {score} upvotes and {comments} comments on Hacker News, indicating significant community interest."

            ts = detail.get('time')
            published = datetime.fromtimestamp(ts, timezone.utc) if ts else None

            return {
                "title": title,
                "url": url,
                "raw_text": raw_text[:1500],
                "published": published,
                "metadata": {
                    "source": "Hacker News",
                    "upvotes": score,
                    "comments": comments,
                    "sector": "tech"
                }
            }
        except Exception as e:
            logger.warning(f"[SCRAPER] Error fetching HN item {sid}: {e}")
        return None

    # Fetch Hacker News details concurrently
    tasks = [asyncio.create_task(fetch_single_story(sid)) for sid in story_ids[:limit*3]]
    for completed_task in asyncio.as_completed(tasks):
        res = await completed_task
        if res:
            items.append(res)
            if len(items) >= limit:
                break
    
    # Cancel remaining tasks
    for t in tasks:
        t.cancel()

    logger.info(f"[SCRAPER] Fetched {len(items)} stories from Hacker News.")
    return items



# ─── Category-Specific RSS Feeds ────────────────────────────────────────────

CATEGORY_FEEDS = {
    "science": [
        "https://www.sciencedaily.com/rss/top/science.xml",
        "https://phys.org/rss-feed/science-news/",
    ],
    "medical": [
        "https://medicalxpress.com/rss-feed/",
        "https://www.sciencedaily.com/rss/health_medicine.xml",
    ],
    "agriculture": [
        "https://news.google.com/rss/search?q=agriculture+OR+farming+OR+crop&hl=en-US&gl=US&ceid=US:en",
    ],
    "weather": [
        "https://news.google.com/rss/search?q=weather+OR+climate+change+OR+natural+disaster&hl=en-US&gl=US&ceid=US:en",
    ],
}

async def fetch_category_rss(category: str, limit: int = 5) -> List[Dict]:
    """Fetches top stories for a specific essential sector using curated RSS feeds."""
    feeds = CATEGORY_FEEDS.get(category, [])
    if not feeds:
        return []
    
    items = []
    tasks = [asyncio.create_task(fetch_rss_feed(feed_url, lookback_hours=48)) for feed_url in feeds]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for fetched in results:
        if isinstance(fetched, list):
            for item in fetched:
                item['metadata'] = {
                    "source": f"RSS ({category})",
                    "sector": category
                }
            items.extend(fetched)
    
    # Deduplicate by title
    seen = set()
    unique = []
    for item in items:
        key = item['title'].lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(item)
    
    return unique[:limit]

# ─── Slot-Based Allocator ───────────────────────────────────────────────────

async def fetch_dynamic_news(limit: int = 5, progress_callback=None) -> List[Dict]:
    """Omnichannel fetcher: pulls from RSS, Reddit, Hacker News, and sector feeds.
    Uses a slot-based allocator to guarantee balanced coverage across sectors.
    
    Slot allocation (5 stories):
      1. The Apex   – absolute top trending story (Reddit/HN by engagement)
      2. Tech       – top tech story from RSS feeds
      3. Science / Medical / Pharma
      4. Agriculture / Weather / Climate
      5. Best remaining from any pool
    """
    logger.info("[SCRAPER] === Phase 2 Omnichannel Fetch Starting ===")
    registry = await load_sent_registry()
    
    # ── 1. Fetch all sources in parallel ─────────────────────────────────
    tech_rss_feeds = [
        "https://techcrunch.com/feed/",
        "https://www.theverge.com/rss/index.xml",
        "https://www.wired.com/feed/rss",
    ]
    
    async def fetch_tech_rss():
        tasks = [asyncio.create_task(fetch_rss_feed(url, 48)) for url in tech_rss_feeds]
        results = await asyncio.gather(*tasks, return_exceptions=True)
        items = []
        for r in results:
            if isinstance(r, list):
                items.extend(r)
        for item in items:
            item.setdefault('metadata', {})['sector'] = 'tech'
        return items

    tech_future = asyncio.create_task(fetch_tech_rss())
    hn_future = asyncio.create_task(fetch_hn_top_stories(limit=8))
    science_future = asyncio.create_task(fetch_category_rss("science", 5))
    medical_future = asyncio.create_task(fetch_category_rss("medical", 5))
    agri_future = asyncio.create_task(fetch_category_rss("agriculture", 5))
    weather_future = asyncio.create_task(fetch_category_rss("weather", 5))

    results = await asyncio.gather(
        tech_future,
        hn_future,
        science_future,
        medical_future,
        agri_future,
        weather_future,
        return_exceptions=True
    )
    
    tech_rss_items = results[0] if isinstance(results[0], list) else []
    hn_items = results[1] if isinstance(results[1], list) else []
    science_items = results[2] if isinstance(results[2], list) else []
    medical_items = results[3] if isinstance(results[3], list) else []
    agri_items = results[4] if isinstance(results[4], list) else []
    weather_items = results[5] if isinstance(results[5], list) else []
    reddit_items = []
    
    # ── 2. Deduplicate against Registry & Intra-batch ────────────────────
    def process_pool(items: List[Dict]) -> List[Dict]:
        filtered = []
        for item in items:
            if not is_duplicate_or_rehash(item['title'], item['url'], registry):
                filtered.append(item)
                # Add to registry instantly to prevent intra-batch dupes
                registry.append({
                    "url": item['url'],
                    "title": item['title'],
                    "token_set": set(WORD_TOKEN_RE.findall(item['title'].lower().strip()))
                })
        return filtered

    social_pool = process_pool(reddit_items + hn_items)
    social_pool.sort(key=lambda x: x.get('metadata', {}).get('upvotes', 0), reverse=True)
    
    tech_pool = process_pool(tech_rss_items)
    science_medical_pool = process_pool(science_items + medical_items)
    agri_weather_pool = process_pool(agri_items + weather_items)
    
    # ── 3. Slot Allocator ────────────────────────────────────────────────
    selected_items = []
    
    async def pick_scrapable_from(pool: List[Dict]) -> Optional[Dict]:
        if not pool:
            return None
        candidates = []
        while pool and len(candidates) < 3:
            candidates.append(pool.pop(0))
        if not candidates:
            return None
        # Try to scrape the candidates in parallel to check if they are blocked/empty
        tasks = [asyncio.create_task(fetch_full_article_text(item['url'])) for item in candidates]
        scraped_texts = await asyncio.gather(*tasks, return_exceptions=True)
        # Find first successfully scraped one
        for idx, text in enumerate(scraped_texts):
            if isinstance(text, str) and len(text.strip()) >= 100:
                item = candidates[idx]
                item['scraped_full_text'] = text
                # Return unused ones back to the pool
                for u_idx in range(len(candidates) - 1, -1, -1):
                    if u_idx != idx:
                        pool.insert(0, candidates[u_idx])
                return item
        # If all fail, return the first one as fallback and return the others
        item = candidates[0]
        for u_idx in range(len(candidates) - 1, 0, -1):
            pool.insert(0, candidates[u_idx])
        return item

    # Slot 1: The Apex
    apex = await pick_scrapable_from(social_pool)
    if apex:
        selected_items.append(apex)
    
    # Slot 2: Tech – top tech RSS story
    tech_pick = await pick_scrapable_from(tech_pool)
    if tech_pick:
        selected_items.append(tech_pick)
    
    # Slot 3: Science / Medical / Pharma
    sci_med_pick = await pick_scrapable_from(science_medical_pool)
    if sci_med_pick:
        selected_items.append(sci_med_pick)
    
    # Slot 4: Agriculture / Weather / Climate
    agri_weather_pick = await pick_scrapable_from(agri_weather_pool)
    if agri_weather_pick:
        selected_items.append(agri_weather_pick)
    
    # Slot 5: Best remaining from ANY pool (round-robin)
    remaining_pools = [social_pool, tech_pool, science_medical_pool, agri_weather_pool]
    while len(selected_items) < limit:
        filled = False
        for pool in remaining_pools:
            pick = await pick_scrapable_from(pool)
            if pick:
                selected_items.append(pick)
                filled = True
                break
        if not filled:
            break  # all pools exhausted
    
    logger.info(f"[SCRAPER] Slot allocator selected {len(selected_items)} stories for AI processing.")
    if progress_callback:
        progress_callback("Writing Summaries", 30, f"Selected {len(selected_items)} articles for AI summarization...")
    
    # ── 4. AI Processing ─────────────────────────────────────────────────
    stories = []
    processed_count = [0]
    
    async def process_item(idx, item):
        # Stagger requests slightly to avoid hitting aggressive instant rate limits
        await asyncio.sleep(idx * 2.5)
        res = await fetch_story_details(item)
        processed_count[0] += 1
        if progress_callback:
            progress = 30 + int((processed_count[0] / len(selected_items)) * 35)
            progress_callback("Writing Summaries", progress, f"Synthesized article {processed_count[0]} of {len(selected_items)}...")
        return res

    tasks = [asyncio.create_task(process_item(idx, item)) for idx, item in enumerate(selected_items)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for res in results:
        if isinstance(res, dict):
            stories.append(res)
                
    if progress_callback:
        progress_callback("Writing Summaries", 65, "AI Summarization completed successfully.", mark_done="Writing Summaries")
    
    return stories

async def fetch_targeted_news(query: str, limit: int = 5, progress_callback=None) -> List[Dict]:
    """Scrapes Google News RSS for a specific topic, bypassing the anti-rehash registry."""
    logger.info(f"[SCRAPER] Fetching targeted news for query: {query}")
    if progress_callback:
        progress_callback("Finding Stories", 15, f"Searching the web for '{query}'...")
    
    # URL encode query safely
    encoded_query = urllib.parse.quote(query)
    rss_feed = f"https://news.google.com/rss/search?q={encoded_query}&hl=en-US&gl=US&ceid=US:en"
    
    raw_items = await fetch_rss_feed(rss_feed, lookback_hours=72)
    
    # Deduplicate by semantic overlap & against history
    registry = await load_sent_registry()
    unique_items = []
    for item in raw_items:
        if not is_duplicate_or_rehash(item['title'], item['url'], registry + unique_items, jaccard_threshold=0.2):
            item['token_set'] = set(WORD_TOKEN_RE.findall(item['title'].lower().strip()))
            unique_items.append(item)
            
    selected_items = unique_items[:limit]
    logger.info(f"Selected {len(selected_items)} targeted stories for AI processing.")
    if progress_callback:
        progress_callback("Writing Summaries", 30, f"Selected {len(selected_items)} articles for AI summarization...", mark_done="Finding Stories")
    
    stories = []
    processed_count = [0]
    
    async def process_item(idx, item):
        # Stagger requests slightly to avoid hitting aggressive instant rate limits
        await asyncio.sleep(idx * 2.5)
        res = await fetch_story_details(item)
        processed_count[0] += 1
        if progress_callback:
            progress = 30 + int((processed_count[0] / len(selected_items)) * 35)
            progress_callback("Writing Summaries", progress, f"Synthesized article {processed_count[0]} of {len(selected_items)}...")
        return res

    tasks = [asyncio.create_task(process_item(idx, item)) for idx, item in enumerate(selected_items)]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    for res in results:
        if isinstance(res, dict):
            stories.append(res)
                
    if progress_callback:
        progress_callback("Writing Summaries", 65, "AI Summarization completed successfully.", mark_done="Writing Summaries")
        
    return stories

async def generate_editorial_synthesis(stories: List[Dict]) -> Dict:
    """Generates an editorial synthesis of all the scraped stories for the RADAR page."""
    if not stories:
        return {
            "meta_theme": "The cost of intelligence is collapsing, the locus of control is shifting, and the moat is moving from models to compute, sovereignty, and energy.",
            "takeaway": "Stop building on a single model. Build the workflow that lets you swap any model in. The cost wall is collapsing. Your moat is the system around the model, not the model itself."
        }

    logger.info("[AI] Generating editorial synthesis for the selected stories...")
    
    # Format the headlines and briefs for the LLM
    stories_text = ""
    for idx, story in enumerate(stories):
        headline = story.get("headline", "News Story")
        brief = story.get("the_brief", "")
        stories_text += f"Story {idx + 1}:\nHeadline: {headline}\nSummary: {brief}\n\n"

    system_prompt = """You are an elite, Pulitzer-winning tech analyst. 
You will be given a list of stories from the last 24 hours. Your job is to analyze them together and find the single, deep macro-trend or pattern that connects them.
You must output ONLY valid JSON matching this exact schema, with no markdown formatting around it:
{
  "meta_theme": "A 2-sentence synthesis of the overarching shift/pattern connecting these stories. Tone must be authoritative, urgent, and punchy.",
  "takeaway": "A 2-sentence actionable warning or advice: what the reader must do to stay ahead, starting with 'Stop building/relying...' or similar imperative verb."
}"""

    user_msg = f"Here is the list of stories to analyze:\n\n{stories_text}"
    
    primary_model = config.OPENROUTER_MODEL
    backup_models = [
        "openai/gpt-oss-120b:free",
        "meta-llama/llama-3.3-70b-instruct:free",
        "google/gemma-4-31b-it:free",
        "openrouter/free"
    ]
    
    content = await _execute_llm_completion(primary_model, system_prompt, user_msg)
    if not content:
        for backup in backup_models:
            logger.info(f"[AI] Synthesis fallback to model: {backup}")
            content = await _execute_llm_completion(backup, system_prompt, user_msg)
            if content:
                break
                
    if content:
        try:
            cleaned_content = content.strip()
            if cleaned_content.startswith("```"):
                lines = cleaned_content.splitlines()
                if lines[0].startswith("```"):
                    lines = lines[1:]
                if lines and lines[-1].startswith("```"):
                    lines = lines[:-1]
                cleaned_content = "\n".join(lines).strip()
            synthesis = json.loads(cleaned_content)
            if "meta_theme" in synthesis and "takeaway" in synthesis:
                logger.info("[AI] Editorial synthesis generated successfully.")
                return {
                    "meta_theme": str(synthesis["meta_theme"]).strip().strip('\'"'),
                    "takeaway": str(synthesis["takeaway"]).strip().strip('\'"')
                }
        except Exception as e:
            logger.warning(f"Failed to parse synthesis JSON: {e}. Raw content: {content}")
            
    return {
        "meta_theme": "The cost of intelligence is collapsing, the locus of control is shifting, and the moat is moving from models to compute, sovereignty, and energy.",
        "takeaway": "Stop building on a single model. Build the workflow that lets you swap any model in. The cost wall is collapsing. Your moat is the system around the model, not the model itself."
    }


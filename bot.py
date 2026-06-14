import os
import asyncio
import logging
from datetime import time, datetime
from typing import Optional
import pytz
from dotenv import load_dotenv

# Load environment variables before importing any other local modules
load_dotenv()

from functools import wraps
from aiohttp import web

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, BotCommandScopeChat
from telegram.ext import Application, ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.error import Forbidden, BadRequest, Conflict, NetworkError, TimedOut, RetryAfter

def safe_handler(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        try:
            return await func(update, context, *args, **kwargs)
        except Exception as e:
            logger.error(f"Error in handler {func.__name__}: {e}", exc_info=True)
            err_msg = "⚠️ *SYSTEM ENCOUNTERED A TEMPORARY HICCUP*\n\nDon't worry, our team has been notified and we are fixing it right away! Please try again in a few moments."
            try:
                if update.callback_query:
                    await update.callback_query.answer("⚠️ An unexpected error occurred. Please try again.", show_alert=True)
                elif update.effective_message:
                    await update.effective_message.reply_text(err_msg, parse_mode="Markdown")
            except Exception as notify_err:
                logger.error(f"Failed to send error notification to user: {notify_err}")
    return wrapper

def admin_only(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = str(update.effective_user.id) if update.effective_user else ""
        admin_id = os.getenv("ADMIN_ID", "6038057345")
        if user_id != admin_id:
            if update.callback_query:
                await update.callback_query.answer("⛔ Unauthorized. Admin access only.", show_alert=True)
            elif update.effective_message:
                await update.effective_message.reply_text("⛔ Unauthorized. Admin access only.")
            return
        return await func(update, context, *args, **kwargs)
    return wrapper

import database
from main import generate_latest_digest, generate_targeted_digest
from config import BRAND_NAME

# Setup logging
logging.Formatter.converter = lambda *args: datetime.now(pytz.timezone('Asia/Kolkata')).timetuple()
logging.basicConfig(
    format="%(asctime)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("telegram.ext.Updater").setLevel(logging.ERROR)
logging.getLogger("telegram.ext._updater").setLevel(logging.ERROR)
logging.getLogger("telegram.ext._utils.networkloop").setLevel(logging.CRITICAL)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Application is used directly to support Python 3.11+ compatibility.

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and handle specific telegram-bot exceptions gracefully."""
    if isinstance(context.error, Conflict):
        logger.warning("Conflict error detected. This usually happens during Render deploys when the new instance starts before the old one fully shuts down. Ignoring.")
    elif isinstance(context.error, (NetworkError, TimedOut)):
        logger.warning(f"Network/Timeout error: {context.error}")
    else:
        logger.error("Exception while handling an update:", exc_info=context.error)

def get_main_menu(first_name: str, is_subscribed: bool = False):
    welcome_text = (
        f"*[ MAIN MENU ]*\n\n"
        f"Welcome to *Ahead of Everyone*, {first_name}!\n"
        f"I am your daily AI-powered tech news assistant.\n\n"
        f"I search through top stories across the tech industry, summarize them, and create a premium daily newsletter just for you.\n\n"
        f"Click below to get today's latest news, or subscribe to receive it automatically every morning at 10 AM IST."
    )
    
    keyboard = [
        [
            InlineKeyboardButton("📰 Get Latest Digest", callback_data="latest"),
            InlineKeyboardButton("ℹ️ About This Bot", callback_data="about")
        ]
    ]
    if is_subscribed:
        keyboard.append([InlineKeyboardButton("🔕 Stop Daily Digests", callback_data="unsubscribe")])
    else:
        keyboard.append([InlineKeyboardButton("🔔 Get Daily Digests", callback_data="subscribe")])
        
    return welcome_text, InlineKeyboardMarkup(keyboard)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message with an inline keyboard."""
    first_name = update.effective_user.first_name or "Reader"
    chat_id = update.effective_chat.id
    is_subscribed = await database.is_subscriber(chat_id)
    welcome_text, reply_markup = get_main_menu(first_name, is_subscribed)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

async def update_loading_message(message, bot, progress_state, topic=None) -> None:
    """Periodically update the loading message based on the real-time progress state from the backend logic."""
    topic_str = f" about *{topic}*" if topic else ""
    chat_id = message.chat_id
    
    # Animated emojis that cycle on each update to show the bot is alive
    ticker_emojis = ["🔄", "⏳", "✨", "⚙️", "🚀", "⚡", "🛰️"]
    idx = 0
    
    while True:
        try:
            # Trigger active chat action status
            progress = progress_state.get("progress", 0)
            action = "upload_document" if progress >= 70 else "typing"
            try:
                await bot.send_chat_action(chat_id=chat_id, action=action)
            except Exception:
                pass
                
            phase = progress_state.get("phase", "Finding Stories")
            detail = progress_state.get("detail", "🌐 Initializing request...")
            done_phases = progress_state.get("done_phases", set())
            
            tick_emoji = ticker_emojis[idx % len(ticker_emojis)]
            idx += 1
            
            # Phase statuses synchronized with actual pipeline progression
            p1_stat = "✅ Done" if "Finding Stories" in done_phases else (f"{tick_emoji} Working..." if phase == "Finding Stories" else "⏳ Waiting")
            p2_stat = "✅ Done" if "Writing Summaries" in done_phases else (f"{tick_emoji} Working..." if phase == "Writing Summaries" else "⏳ Waiting")
            p3_stat = "✅ Done" if "Creating PDF" in done_phases else (f"{tick_emoji} Working..." if phase == "Creating PDF" else "⏳ Waiting")
            p4_stat = "✅ Done" if "Delivering" in done_phases else (f"{tick_emoji} Working..." if phase == "Delivering" else "⏳ Waiting")
            
            filled_length = int(progress / 5)
            gauge = "█" * filled_length + "░" * (20 - filled_length)
            
            text = (
                f"{tick_emoji} *{BRAND_NAME.upper()}* | Preparing Newsletter\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🌐 *Finding Stories:*     {p1_stat}\n"
                f"✍️ *Writing Summaries:*   {p2_stat}\n"
                f"🎨 *Creating PDF:*       {p3_stat}\n"
                f"🚀 *Delivering:*         {p4_stat}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"{detail}\n\n"
                f"`[{gauge}]`  *{progress}%*\n\n"
                f"⏳ Fetching custom news{topic_str}. Just a moment!"
            )
            
            try:
                await message.edit_text(text=text, parse_mode="Markdown")
            except Exception as edit_err:
                # Suppress "Message is not modified" spam
                if "not modified" not in str(edit_err).lower():
                    logger.warning(f"Failed to edit progress message: {edit_err}")
            
            await asyncio.sleep(2)
        except asyncio.CancelledError:
            break
        except Exception as e:
            logger.error(f"Error in update_loading_message: {e}")
            await asyncio.sleep(2)


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline keyboard button clicks."""
    query = update.callback_query
    await query.answer()
    
    chat_id = query.message.chat_id
    action = query.data
    
    is_media = bool(query.message.document or query.message.photo or query.message.video)

    async def edit_or_reply(text, reply_markup=None):
        if is_media:
            try:
                await query.edit_message_reply_markup(reply_markup=None)
            except Exception:
                pass
            return await context.bot.send_message(chat_id=chat_id, text=text, reply_markup=reply_markup, parse_mode="Markdown")
        else:
            await query.edit_message_text(text=text, reply_markup=reply_markup, parse_mode="Markdown")
            return query.message
            
    if action == "latest":
        chat_id = query.message.chat_id
        
        is_subscribed = await database.is_subscriber(chat_id)
        if is_subscribed:
            keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]]
        else:
            keyboard = [
                [InlineKeyboardButton("🔔 Get Daily Digests", callback_data="subscribe")],
                [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        cached_file_id = await database.get_cached_file_id_exact("latest")
        if cached_file_id:
            caption = f"✅ *NEWS READY* | Here is your daily newsletter! Enjoy reading."
            try:
                await context.bot.send_document(chat_id=chat_id, document=cached_file_id, caption=caption, parse_mode="Markdown", reply_markup=reply_markup)
                try:
                    if is_media:
                        await query.edit_message_reply_markup(reply_markup=None)
                    else:
                        await query.message.delete()
                except Exception as e:
                    logger.debug(f"Could not handle old query message: {e}")
                return
            except Exception as e:
                logger.warning(f"Failed to send cached file_id, generating fresh: {e}")
                
        loading_msg = await edit_or_reply(text="⏳ *FETCHING NEWS* | Searching for the latest tech stories... Just a moment!")
        
        await enqueue_generation(chat_id, None, loading_msg, context.application, is_subscribed)
            
    elif action == "subscribe":
        added = await database.add_subscriber(chat_id)
        if added:
            keyboard = [
                [InlineKeyboardButton("📰 Get Latest Digest", callback_data="latest")],
                [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]
            ]
            await edit_or_reply(text="✅ *SUBSCRIBED* | You will now receive daily news updates automatically.", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            back_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]])
            await edit_or_reply(text="ℹ️ *ALREADY SUBSCRIBED* | You are already receiving daily updates.", reply_markup=back_keyboard)
            
    elif action == "unsubscribe":
        removed = await database.remove_subscriber(chat_id)
        if removed:
            keyboard = [
                [InlineKeyboardButton("🔔 Re-Subscribe", callback_data="subscribe")],
                [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]
            ]
            await edit_or_reply(text="🔕 *UNSUBSCRIBED* | You will no longer receive daily news automatically.", reply_markup=InlineKeyboardMarkup(keyboard))
        else:
            back_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]])
            await edit_or_reply(text="ℹ️ *NOT SUBSCRIBED* | You are not currently subscribed to daily updates.", reply_markup=back_keyboard)
            
    elif action == "about":
        about_text = (
            f"*[ ABOUT THIS BOT ]*\n\n"
            f"This bot is powered by smart AI. It automatically searches for major news stories, rewrites them to be quick and easy to read, and designs a premium PDF newsletter just for you."
        )
        is_subscribed = await database.is_subscriber(chat_id)
        keyboard = [[InlineKeyboardButton("📰 Get Latest Digest", callback_data="latest")]]
        if is_subscribed:
            keyboard.append([InlineKeyboardButton("🔕 Stop Daily Digests", callback_data="unsubscribe")])
        else:
            keyboard.append([InlineKeyboardButton("🔔 Get Daily Digests", callback_data="subscribe")])
        keyboard.append([InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")])
        
        await edit_or_reply(text=about_text, reply_markup=InlineKeyboardMarkup(keyboard))
        
    elif action == "main_menu":
        first_name = query.from_user.first_name or "Reader"
        is_subscribed = await database.is_subscriber(chat_id)
        welcome_text, reply_markup = get_main_menu(first_name, is_subscribed)
        await edit_or_reply(text=welcome_text, reply_markup=reply_markup)
        
    elif action in ["admin_stats", "admin_broadcast"]:
        user_id = str(query.from_user.id)
        admin_id = os.getenv("ADMIN_ID", "6038057345")
        if user_id != admin_id:
            await query.answer("⛔ Unauthorized. Admin access only.", show_alert=True)
            return
            
        if action == "admin_stats":
            subscribers = await database.get_all_subscribers()
            stats_text = (
                f"📊 *Admin Statistics*\n\n"
                f"👥 Total Subscribers: {len(subscribers)}\n"
                f"🕒 Server Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC"
            )
            keyboard = [
                [
                    InlineKeyboardButton("📢 Broadcast Now", callback_data="admin_broadcast"),
                    InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await edit_or_reply(text=stats_text, reply_markup=reply_markup)
            
        elif action == "admin_broadcast":
            progress_state = {
                "phase": "Finding Stories",
                "progress": 0,
                "detail": "🌐 Initializing global broadcast...",
                "done_phases": set()
            }
            
            def progress_callback(phase, progress, detail, mark_done=None):
                progress_state["phase"] = phase
                progress_state["progress"] = progress
                progress_state["detail"] = detail
                if mark_done:
                    progress_state["done_phases"].add(mark_done)
                    
            loading_msg = await edit_or_reply(text="⏳ Preparing global broadcast. Please standby...")
            ticker_task = asyncio.create_task(update_loading_message(loading_msg, context, progress_state))
            try:
                await scheduled_broadcast(context, force_fresh=True, progress_callback=progress_callback)
            except Exception as e:
                if "cancelled by admin" in str(e).lower():
                    logger.info("Admin broadcast button callback cancelled.")
                else:
                    raise e
            finally:
                ticker_task.cancel()
                try:
                    await ticker_task
                except asyncio.CancelledError:
                    pass
                try:
                    await loading_msg.delete()
                except Exception:
                    pass
                    
            if context.bot_data.get("broadcast_cancelled", False):
                await context.bot.send_message(chat_id=chat_id, text="🛑 *BROADCAST ABORTED*", parse_mode="Markdown")
                return
                
            keyboard = [
                [
                    InlineKeyboardButton("📊 View Stats", callback_data="admin_stats"),
                    InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(chat_id=chat_id, text="✅ Global broadcast completed successfully!", reply_markup=reply_markup, parse_mode="Markdown")

import uuid

async def update_queue_status(message, bot, chat_id: int, queue_list: list):
    """Dynamically updates the waiting message for users in the queue."""
    ticker_emojis = ["🔄", "⏳", "✨", "⚙️", "🚀", "⚡", "🛰️"]
    idx = 0
    while True:
        try:
            if chat_id not in queue_list:
                break
                
            position = queue_list.index(chat_id) + 1
            est_wait = position * 45  # roughly 45s per generation
            
            gauge_len = 16
            filled = idx % gauge_len
            gauge = "░" * filled + "█" * 3 + "░" * (gauge_len - filled - 3)
            if len(gauge) > gauge_len:
                gauge = gauge[:gauge_len]
            
            tick_emoji = ticker_emojis[idx % len(ticker_emojis)]
            idx += 1
            
            text = (
                f"{tick_emoji} *YOU ARE IN LINE* | Please hold!\n\n"
                f"You are currently in position #{position} in the queue to prevent server overload.\n"
                f"Estimated wait time: ~{est_wait} seconds.\n\n"
                f"[{gauge}] waiting...\n\n"
                f"_(Too long? You can click /cancel to abort and save resources)_"
            )
            
            await message.edit_text(text=text, parse_mode="Markdown")
            await asyncio.sleep(2.5)
        except Exception:
            await asyncio.sleep(2.5)

async def enqueue_generation(chat_id: int, query: Optional[str], message, app: Application, is_subscribed: bool):
    """Adds a generation job to the global FIFO queue."""
    job_id = str(uuid.uuid4())
    job = {
        "job_id": job_id,
        "chat_id": chat_id,
        "query": query, # None for Latest Digest
        "message": message,
        "is_subscribed": is_subscribed
    }
    
    app.bot_data.setdefault("queue_list", []).append(chat_id)
    app.bot_data.setdefault("active_user_generations", {})[chat_id] = False
    
    await app.bot_data["request_queue"].put(job)
    asyncio.create_task(update_queue_status(message, app.bot, chat_id, app.bot_data["queue_list"]))

async def queue_worker(app: Application):
    """Background task that processes the queue sequentially (1 at a time)."""
    while True:
        job = await app.bot_data["request_queue"].get()
        chat_id = job["chat_id"]
        
        queue_list = app.bot_data.get("queue_list", [])
        if chat_id in queue_list:
            queue_list.remove(chat_id)
            
        if app.bot_data.get("active_user_generations", {}).get(chat_id, False):
            logger.info(f"[QUEUE] Skipped cancelled job {job['job_id']} for chat {chat_id}.")
            app.bot_data["request_queue"].task_done()
            continue
            
        query = job["query"]
        message = job["message"]
        is_subscribed = job["is_subscribed"]
        
        target_name = f"'{query}'" if query else "Latest Digest"
        logger.info(f"[QUEUE] Started processing job {job['job_id']} for {target_name} (Chat: {chat_id})")
        
        progress_state = {
            "phase": "Finding Stories",
            "progress": 0,
            "detail": f"🌐 Initializing search...",
            "done_phases": set()
        }
        
        def progress_callback(phase, progress, detail, mark_done=None):
            if app.bot_data.get("active_user_generations", {}).get(chat_id, False):
                raise RuntimeError("Generation cancelled by user.")
            progress_state["phase"] = phase
            progress_state["progress"] = progress
            progress_state["detail"] = detail
            if mark_done:
                progress_state["done_phases"].add(mark_done)
                
        ticker_task = asyncio.create_task(update_loading_message(message, app.bot, progress_state, topic=query))
        
        pdf_filename = None
        cached_file_id = None
        try:
            # Double-check cache right before generation to prevent redundant duplicate jobs
            if query:
                cached_file_id = await database.get_cached_file_id_semantic(query)
            else:
                cached_file_id = await database.get_cached_file_id_exact("latest")
                
            if cached_file_id:
                logger.info(f"[QUEUE] Double-check hit! Found cached PDF for {target_name}. Skipping generation.")
                progress_state["phase"] = "Creating PDF"
                progress_state["done_phases"].update(["Finding Stories", "Writing Summaries"])
                progress_state["progress"] = 90
                progress_state["detail"] = "Cached digest retrieved, starting delivery..."
            else:
                if query:
                    pdf_filename = await generate_targeted_digest(query, 5, progress_callback)
                else:
                    pdf_filename = await generate_latest_digest(5, progress_callback)
        except Exception as e:
            if "cancelled by user" in str(e).lower():
                logger.info(f"[QUEUE] User {chat_id} cancelled the generation during processing.")
            else:
                logger.error(f"[QUEUE] Error during queued generation: {e}")
        finally:
            ticker_task.cancel()
            try:
                await ticker_task
            except asyncio.CancelledError:
                pass
            try:
                await message.delete()
            except Exception as e:
                logger.error(f"Failed to delete queue/loading message: {e}")
            app.bot_data.get("active_user_generations", {}).pop(chat_id, None)
            
        if app.bot_data.get("active_user_generations", {}).get(chat_id, False):
            back_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]])
            await app.bot.send_message(chat_id=chat_id, text="🛑 *GENERATION ABORTED*", reply_markup=back_keyboard, parse_mode="Markdown")
        else:
            if cached_file_id or (pdf_filename and os.path.exists(pdf_filename)):
                try:
                    caption = f"✅ *NEWS READY* | Here is your daily newsletter! Enjoy reading."
                    if query:
                        caption = f"✅ *SEARCH FINISHED* | Sending your newsletter about *{query}*..."
                        
                    pretty_filename = os.path.basename(pdf_filename).replace("_", " ") if pdf_filename else "AoE_Tech_News.pdf"
                    if is_subscribed:
                        keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]]
                    else:
                        keyboard = [
                            [InlineKeyboardButton("🔔 Get Daily Digests", callback_data="subscribe")],
                            [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]
                        ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    
                    if cached_file_id:
                        msg = await app.bot.send_document(chat_id=chat_id, document=cached_file_id, caption=caption, parse_mode="Markdown", reply_markup=reply_markup)
                    else:
                        with open(pdf_filename, "rb") as file:
                            msg = await app.bot.send_document(chat_id=chat_id, document=file, filename=pretty_filename, caption=caption, parse_mode="Markdown", reply_markup=reply_markup)
                            if msg and msg.document:
                                if query:
                                    await database.set_cached_file_id_semantic(query, msg.document.file_id)
                                else:
                                    await database.set_cached_file_id_exact("latest", msg.document.file_id)
                finally:
                    if pdf_filename:
                        try:
                            os.remove(pdf_filename)
                        except Exception as e:
                            logger.error(f"[QUEUE] Failed to delete {pdf_filename}: {e}")
            else:
                logger.warning(f"[QUEUE] Generation failed/not found for {target_name}.")
                back_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]])
                await app.bot.send_message(chat_id=chat_id, text=f"😔 *NOT FOUND* | Sorry, I couldn't find enough news right now. Try another topic!", reply_markup=back_keyboard, parse_mode="Markdown")
                
        logger.info(f"[QUEUE] Finished processing job {job['job_id']}")
        app.bot_data["request_queue"].task_done()


async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /news command to fetch targeted news using semantic matching."""
    query = " ".join(context.args)
    chat_id = update.message.chat_id
    
    logger.info(f"[BOT] User {chat_id} invoked /news with query: '{query}'")
    
    if not query:
        back_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]])
        await update.message.reply_text("Please specify a topic! Example: `/news space exploration`", reply_markup=back_keyboard, parse_mode="Markdown")
        return
        
    cached_file_id = await database.get_cached_file_id_semantic(query)
    if cached_file_id:
        caption = f"✅ *SEARCH FINISHED* | Sending your newsletter about *{query}*..."
        is_subscribed = await database.is_subscriber(chat_id)
        if is_subscribed:
            keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]]
        else:
            keyboard = [
                [InlineKeyboardButton("🔔 Get Daily Digests", callback_data="subscribe")],
                [InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await context.bot.send_document(chat_id=chat_id, document=cached_file_id, caption=caption, parse_mode="Markdown", reply_markup=reply_markup)
            return
        except Exception as e:
            logger.warning(f"Failed to send cached targeted file_id, generating fresh: {e}")
            
    is_subscribed = await database.is_subscriber(chat_id)
    loading_msg = await update.message.reply_text(f"⏳ *FETCHING NEWS* | Finding stories about *{query}*... Just a moment!", parse_mode="Markdown")
    
    await enqueue_generation(chat_id, query, loading_msg, context.application, is_subscribed)

@admin_only
async def admin_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /admin_stats command."""
    logger.info(f"[BOT] Admin {update.effective_user.id} invoked /admin_stats")
    subscribers = await database.get_all_subscribers()
    stats_text = (
        f"*[ SYSTEM STATUS ]*\n\n"
        f"👥 *Total Subscribers:* {len(subscribers)}\n"
        f"⏱️ *Server Time:* {datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')} IST"
    )
    keyboard = [
        [
            InlineKeyboardButton("📢 Broadcast Now", callback_data="admin_broadcast"),
            InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(stats_text, reply_markup=reply_markup, parse_mode="Markdown")

@admin_only
async def admin_broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Force an immediate daily broadcast (Admin Only)."""
    chat_id = update.message.chat_id
    logger.info(f"[BOT] Admin {chat_id} invoked /broadcast")

    progress_state = {
        "phase": "Finding Stories",
        "progress": 0,
        "detail": "🌐 Initializing global broadcast...",
        "done_phases": set()
    }
    
    def progress_callback(phase, progress, detail, mark_done=None):
        progress_state["phase"] = phase
        progress_state["progress"] = progress
        progress_state["detail"] = detail
        if mark_done:
            progress_state["done_phases"].add(mark_done)
            
    loading_msg = await update.message.reply_text("⏳ *PREPARING* | Getting today's newsletter ready for everyone...", parse_mode="Markdown")
    ticker_task = asyncio.create_task(update_loading_message(loading_msg, context, progress_state))
    try:
        await scheduled_broadcast(context, force_fresh=True, progress_callback=progress_callback)
    except Exception as e:
        if "cancelled by admin" in str(e).lower():
            logger.info("Admin broadcast command cancelled.")
        else:
            raise e
    finally:
        ticker_task.cancel()
        try:
            await ticker_task
        except asyncio.CancelledError:
            pass
        try:
            await loading_msg.delete()
        except Exception:
            pass
            
    if context.bot_data.get("broadcast_cancelled", False):
        await update.message.reply_text("🛑 *BROADCAST ABORTED*", parse_mode="Markdown")
        return
        
    keyboard = [
        [
            InlineKeyboardButton("📊 View Stats", callback_data="admin_stats"),
            InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("✅ *SENT* | Newsletter successfully delivered to all subscribers!", reply_markup=reply_markup, parse_mode="Markdown")

async def cancel_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Cancel the current running global broadcast or individual user generation."""
    logger.info(f"[BOT] User {update.effective_user.id} invoked /cancel")
    chat_id = update.effective_chat.id if update.effective_chat else None
    if not chat_id:
        return
        
    user_id = str(update.effective_user.id) if update.effective_user else ""
    admin_id = os.getenv("ADMIN_ID", "6038057345")
    is_admin = (user_id == admin_id)
    
    # 1. Admin trying to cancel global broadcast
    if is_admin and context.bot_data.get("broadcast_in_progress", False):
        context.bot_data["broadcast_cancelled"] = True
        await update.message.reply_text("🛑 *CANCELLATION REQUESTED* | Halting the active broadcast pipeline. Standby...")
        return
        
    # 2. Check if this specific user has an active generation running
    active_gens = context.bot_data.get("active_user_generations", {})
    if chat_id in active_gens:
        active_gens[chat_id] = True
        await update.message.reply_text("🛑 *CANCELLATION REQUESTED* | Halting your active pipeline. Standby...")
        return
        
    await update.message.reply_text("ℹ️ No active generation is currently running for your session.")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command with context-specific inline keyboard."""
    logger.info(f"[BOT] User {update.effective_user.id} invoked /help")
    user_id = str(update.effective_user.id) if update.effective_user else ""
    admin_id = os.getenv("ADMIN_ID", "6038057345")
    is_admin = user_id == admin_id
    
    help_text = (
        f"*[ HELP & COMMANDS ]*\n"
        f"Here is what I can do for you:\n\n"
        f"⚡ `/start` » Open the main menu\n"
        f"🌐 `/news <topic>` » Search for news on a specific topic\n"
        f"📖 `/help` » Read this help guide\n\n"
    )
    
    if is_admin:
        help_text += (
            f"⚙️ *Admin Commands:*\n"
            f"• `/status` » Check if the system is running well\n"
            f"• `/stats` » View total number of subscribers\n"
            f"• `/broadcast` » Send today's newsletter to everyone\n\n"
        )
    
    keyboard = [
        [
            InlineKeyboardButton("📰 Get Latest Digest", callback_data="latest"),
            InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
        ]
    ]
    if is_admin:
        keyboard.append([
            InlineKeyboardButton("📊 View Stats", callback_data="admin_stats"),
            InlineKeyboardButton("📢 Broadcast Now", callback_data="admin_broadcast")
        ])
        
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(help_text, reply_markup=reply_markup, parse_mode="Markdown")

@admin_only
async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /status command (Admin Only)."""
    logger.info(f"[BOT] Admin {update.effective_user.id} invoked /status")
    chat_id = update.message.chat_id
    
    # Check database connection state
    try:
        pool = await database.get_pool()
        db_ok = pool is not None
    except Exception:
        db_ok = False
        
    db_status = "🟢 Operational" if db_ok else "🔴 Offline"
    
    # Check current user subscription status
    subscribed = False
    if db_ok:
        try:
            subscribers = await database.get_all_subscribers()
            subscribed = chat_id in subscribers
        except Exception:
            pass
            
    sub_status = "🔔 Subscribed" if subscribed else "🔕 Not Subscribed"
    
    status_text = (
        f"*[ SYSTEM STATUS ]*\n\n"
        f"⚙️ *Database:* {db_status}\n"
        f"👤 *Subscription:* {sub_status}\n"
        f"⏱️ *Server Time:* {datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')} IST"
    )
    
    # Include buttons to easily return or manage admin options
    keyboard = [
        [
            InlineKeyboardButton("📊 View Stats", callback_data="admin_stats"),
            InlineKeyboardButton("📢 Broadcast Now", callback_data="admin_broadcast")
        ],
        [
            InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(status_text, reply_markup=reply_markup, parse_mode="Markdown")

async def general_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all other text messages."""
    text = (
        "*[ INVALID COMMAND ]*\n\n"
        "Sorry, I don't understand that command. Use `/start` to see the main menu, or find news on a specific topic using `/news <topic>`.\n\n"
        "Example: `/news new smartphones`"
    )
    back_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]])
    await update.message.reply_text(text, reply_markup=back_keyboard, parse_mode="Markdown")

async def scheduled_broadcast(context: ContextTypes.DEFAULT_TYPE, force_fresh: bool = False, progress_callback=None) -> None:
    """Scheduled job to generate the daily digest and send it to all subscribers."""
    logger.info(f"[SCHEDULER] Starting scheduled daily broadcast... (force_fresh={force_fresh})")
    context.bot_data["broadcast_in_progress"] = True
    context.bot_data["broadcast_cancelled"] = False
    
    pdf_filename = None
    try:
        if progress_callback:
            if context.bot_data.get("broadcast_cancelled", False):
                raise RuntimeError("Broadcast cancelled by admin.")
            progress_callback("Finding Stories", 5, "Initializing subscriber database connections...")
        
        subscribers = await database.get_all_subscribers()
        if not subscribers:
            admin_id = os.getenv("ADMIN_ID", "6038057345")
            if admin_id:
                try:
                    subscribers = [int(admin_id)]
                    logger.info(f"No subscribers in DB. Defaulting to admin ID {admin_id} for performance check.")
                except ValueError:
                    pass
                    
        if not subscribers:
            logger.info("No subscribers found for broadcast. Skipping execution.")
            if progress_callback:
                progress_callback("Delivering", 100, "No subscribers found. Skipping broadcast.", mark_done="Finding Stories")
            return
            
        cached_file_id = None if force_fresh else await database.get_cached_file_id_exact("latest")
        
        if cached_file_id:
            logger.info("Using cached latest digest for scheduled broadcast.")
            if progress_callback:
                if context.bot_data.get("broadcast_cancelled", False):
                    raise RuntimeError("Broadcast cancelled by admin.")
                progress_callback("Delivering", 90, "Cached digest retrieved, starting delivery...", mark_done="Finding Stories")
                progress_callback("Delivering", 90, "Cached digest retrieved, starting delivery...", mark_done="Writing Summaries")
                progress_callback("Delivering", 90, "Cached digest retrieved, starting delivery...", mark_done="Creating PDF")
        else:
            pdf_filename = await generate_latest_digest(5, progress_callback)
            if not pdf_filename or not os.path.exists(pdf_filename):
                logger.error("Failed to generate PDF for broadcast.")
                if progress_callback:
                    progress_callback("Delivering", 100, "⚠️ Generation failed.", mark_done="Delivering")
                return
                
        caption = f"📰 *{BRAND_NAME}* | Digest for {datetime.now().strftime('%b %d, %Y')}\n\nInnovating the future, today."
        
        success_count = 0
        pretty_filename = None
        if pdf_filename:
            pretty_filename = os.path.basename(pdf_filename).replace("_", " ")
            
        for idx, chat_id in enumerate(subscribers):
            # Check for cancellation before sleeping or sending
            if context.bot_data.get("broadcast_cancelled", False):
                raise RuntimeError("Broadcast cancelled by admin.")
                
            # 0.05 seconds delay between sends to prevent hitting Telegram limits
            await asyncio.sleep(0.05)
            
            if progress_callback:
                progress = 90 + int((idx / len(subscribers)) * 9)
                progress_callback("Delivering", progress, f"Broadcasting newsletter to subscriber {idx + 1} of {len(subscribers)}...")
                
            sent = False
            for attempt in range(3):
                if context.bot_data.get("broadcast_cancelled", False):
                    raise RuntimeError("Broadcast cancelled by admin.")
                try:
                    if cached_file_id:
                        await context.bot.send_document(chat_id=chat_id, document=cached_file_id, caption=caption, parse_mode="Markdown")
                    else:
                        with open(pdf_filename, "rb") as file:
                            msg = await context.bot.send_document(chat_id=chat_id, document=file, filename=pretty_filename, caption=caption, parse_mode="Markdown")
                            if msg and msg.document:
                                cached_file_id = msg.document.file_id
                                await database.set_cached_file_id_exact("latest", cached_file_id)
                    success_count += 1
                    sent = True
                    break
                except RetryAfter as e:
                    logger.warning(f"Telegram rate limit hit (RetryAfter). Sleeping for {e.retry_after}s (attempt {attempt + 1}/3)...")
                    await asyncio.sleep(e.retry_after)
                except Forbidden:
                    logger.warning(f"User {chat_id} blocked the bot. Removing subscriber.")
                    await database.remove_subscriber(chat_id)
                    break
                except BadRequest as e:
                    if "chat not found" in str(e).lower():
                        logger.warning(f"Chat {chat_id} not found. Removing subscriber.")
                        await database.remove_subscriber(chat_id)
                    else:
                        logger.error(f"Failed to send to {chat_id} (BadRequest): {e}")
                    break
                except (NetworkError, TimedOut) as e:
                    logger.warning(f"Network error/timeout sending to {chat_id} (attempt {attempt + 1}/3): {e}")
                    if attempt < 2:
                        await asyncio.sleep(1)
                    else:
                        logger.error(f"Failed to send to {chat_id} after all retries: {e}")
                except Exception as e:
                    logger.error(f"Failed to send to {chat_id} due to unexpected error: {e}")
                    break
                
        logger.info(f"Broadcast completed. Sent to {success_count}/{len(subscribers)} subscribers.")
        if progress_callback:
            progress_callback("Delivering", 100, f"Global broadcast complete! Distributed to {success_count} subscribers.", mark_done="Delivering")
    finally:
        context.bot_data["broadcast_in_progress"] = False
        if pdf_filename:
            try:
                os.remove(pdf_filename)
            except Exception as e:
                logger.error(f"Failed to clean up broadcast PDF {pdf_filename}: {e}")

async def post_init(app: Application) -> None:
    """Initialize the database during bot startup."""
    await database.init_db()
    
    app.bot_data['request_queue'] = asyncio.Queue()
    app.bot_data['queue_list'] = []
    app.bot_data['queue_worker_task'] = asyncio.create_task(queue_worker(app))
    
    # Register global/default commands for all users
    try:
        global_commands = [
            BotCommand("start", "🚀 Greet & show menu"),
            BotCommand("news", "📰 Fetch news (e.g., /news AI)"),
            BotCommand("help", "📖 Show help manual"),
            BotCommand("cancel", "🛑 Cancel active generation")
        ]
        success_global = await app.bot.set_my_commands(global_commands)
        logger.info(f"Telegram set_my_commands (global) API response: {success_global}")
    except Exception as e:
        logger.error(f"Failed to register global commands: {e}")
        
    # Register admin-scoped commands dynamically on startup
    try:
        admin_id = os.getenv("ADMIN_ID", "6038057345")
        if admin_id:
            try:
                admin_chat_id = int(admin_id)
                admin_commands = [
                    BotCommand("start", "🚀 Greet & show menu"),
                    BotCommand("news", "📰 Fetch news (e.g., /news AI)"),
                    BotCommand("status", "🖥️ Check system status"),
                    BotCommand("help", "📖 Show help menu"),
                    BotCommand("stats", "📊 View subscriber stats"),
                    BotCommand("broadcast", "📢 Force immediate broadcast"),
                    BotCommand("cancel", "🛑 Cancel active broadcast/generation")
                ]
                success = await app.bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=admin_chat_id))
                logger.info(f"Telegram set_my_commands (admin) API response: {success}")
                
                # Verify registration
                registered = await app.bot.get_my_commands(scope=BotCommandScopeChat(chat_id=admin_chat_id))
                logger.info(f"Verified registered commands for admin {admin_chat_id}: {[cmd.command for cmd in registered]}")
            except ValueError:
                logger.warning(f"Invalid ADMIN_ID format: {admin_id}")
    except Exception as e:
        logger.error(f"Failed to register admin-scoped commands with Telegram: {e}")

async def post_stop(app: Application) -> None:
    """Gracefully close external resources."""
    worker = app.bot_data.get('queue_worker_task')
    if worker:
        worker.cancel()
        try:
            await worker
        except asyncio.CancelledError:
            pass
    await database.close_db()

def build_bot() -> Application:
    """Build the bot application."""
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set in environment variables!")
        exit(1)
        
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .post_init(post_init)
        .post_stop(post_stop)
        .concurrent_updates(True)
        .build()
    )
    
    app.add_handler(CommandHandler("start", safe_handler(start_command)))
    app.add_handler(CommandHandler("news", safe_handler(news_command)))
    app.add_handler(CommandHandler("status", safe_handler(status_command)))
    app.add_handler(CommandHandler("help", safe_handler(help_command)))
    app.add_handler(CommandHandler("broadcast", safe_handler(admin_broadcast_command)))
    app.add_handler(CommandHandler("stats", safe_handler(admin_stats_command)))
    app.add_handler(CommandHandler("admin_stats", safe_handler(admin_stats_command)))
    app.add_handler(CommandHandler("admin_broadcast", safe_handler(admin_broadcast_command)))
    app.add_handler(CommandHandler("cancel", safe_handler(cancel_command)))
    app.add_handler(CommandHandler("cancel_broadcast", safe_handler(cancel_command)))
    app.add_handler(CallbackQueryHandler(safe_handler(button_handler)))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, safe_handler(general_message_handler)))
    
    # Register global error handler
    app.add_error_handler(error_handler)
    
    # Schedule the daily broadcast at 10:00 AM IST (Asia/Kolkata)
    # Using python-telegram-bot's built-in job queue
    job_queue = app.job_queue
    ist_tz = pytz.timezone('Asia/Kolkata')
    broadcast_time = time(hour=10, minute=0, tzinfo=ist_tz)
    job_queue.run_daily(scheduled_broadcast, broadcast_time)
    
    return app

if __name__ == "__main__":
    app = build_bot()
    webhook_url = os.environ.get("WEBHOOK_URL")
    
    if webhook_url:
        port = int(os.environ.get("PORT", "10000"))
        logger.info(f"Starting bot in WEBHOOK mode on port {port}...")
        app.run_webhook(
            listen="0.0.0.0",
            port=port,
            webhook_url=webhook_url,
            drop_pending_updates=True
        )
    else:
        logger.info("No WEBHOOK_URL detected. Starting bot in POLLING mode. Press Ctrl+C to stop.")
        app.run_polling(drop_pending_updates=True)

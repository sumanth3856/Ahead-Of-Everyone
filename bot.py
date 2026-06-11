import os
import asyncio
import logging
from datetime import time, datetime
import pytz
from dotenv import load_dotenv

# Load environment variables before importing any other local modules
load_dotenv()

from functools import wraps
from aiohttp import web

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, BotCommandScopeChat
from telegram.ext import Application, ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.error import Forbidden, BadRequest

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
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Application is used directly to support Python 3.11+ compatibility.

def get_main_menu(first_name: str):
    welcome_text = (
        f"*[ INITIALIZING SECURE CONNECTION... ]*\n\n"
        f"Welcome to *Ahead of Everyone*.\n"
        f"You are now tapped into the daily autonomous tech intelligence feed.\n\n"
        f"I process thousands of raw data points across the tech industry to deliver the absolute apex of daily news—curated, summarized, and formatted into a premium intelligence brief.\n\n"
        f"Click below to generate your first tactical briefing, or subscribe to get it automatically delivered every morning at 10 AM IST."
    )
    
    keyboard = [
        [
            InlineKeyboardButton("📰 Get Latest Digest", callback_data="latest"),
            InlineKeyboardButton("ℹ️ About This Bot", callback_data="about")
        ],
        [
            InlineKeyboardButton("🔔 Get Daily Digests", callback_data="subscribe"),
            InlineKeyboardButton("🔕 Stop Daily Digests", callback_data="unsubscribe")
        ]
    ]
    return welcome_text, InlineKeyboardMarkup(keyboard)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message with an inline keyboard."""
    first_name = update.effective_user.first_name or "Reader"
    welcome_text, reply_markup = get_main_menu(first_name)
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

async def update_loading_message(message, context, topic=None) -> None:
    """Periodically update the loading message and trigger active chat actions to keep the user engaged."""
    phases = [
        {"name": "Finding Stories", "progress": 15, "detail": "🌐 Connecting to news outlets..."},
        {"name": "Finding Stories", "progress": 25, "detail": "🔍 Searching the web for the latest updates..."},
        {"name": "Writing Summaries", "progress": 40, "detail": "✂️ Sorting through stories to pick the best ones..."},
        {"name": "Writing Summaries", "progress": 55, "detail": "✍️ Writing clear summaries and key highlights..."},
        {"name": "Creating PDF", "progress": 70, "detail": "🎨 Formatting the pages into a clean magazine layout..."},
        {"name": "Creating PDF", "progress": 85, "detail": "✨ Putting the final touches on your newsletter..."},
        {"name": "Delivering", "progress": 95, "detail": "🚀 Sending the PDF file straight to your chat..."}
    ]
    
    idx = 0
    topic_str = f" about *{topic}*" if topic else ""
    chat_id = message.chat_id
    
    # Emojis that change on each tick to create an animated feel
    ticker_emojis = ["🔄", "⏳", "✨", "⚙️", "🚀", "⚡", "🛰️"]
    
    while True:
        try:
            # Trigger active chat action status (lasts ~5 seconds in Telegram client)
            action = "upload_document" if idx >= 4 else "typing"
            try:
                await context.bot.send_chat_action(chat_id=chat_id, action=action)
            except Exception:
                pass
                
            await asyncio.sleep(8)
            current = phases[idx % len(phases)]
            tick_emoji = ticker_emojis[idx % len(ticker_emojis)]
            
            p1_stat = "✅ Done" if idx >= 2 else f"{tick_emoji} Working..."
            p2_stat = "✅ Done" if idx >= 4 else (f"{tick_emoji} Working..." if idx >= 2 else "⏳ Waiting")
            p3_stat = "✅ Done" if idx >= 6 else (f"{tick_emoji} Working..." if idx >= 4 else "⏳ Waiting")
            p4_stat = "✅ Done" if idx >= 7 else (f"{tick_emoji} Working..." if idx >= 6 else "⏳ Waiting")
            
            filled_length = int(current["progress"] / 5)
            gauge = "█" * filled_length + "░" * (20 - filled_length)
            
            text = (
                f"{tick_emoji} *{BRAND_NAME.upper()}* | Preparing Newsletter\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n"
                f"🌐 *Finding Stories:*     {p1_stat}\n"
                f"✍️ *Writing Summaries:*   {p2_stat}\n"
                f"🎨 *Creating PDF:*       {p3_stat}\n"
                f"🚀 *Delivering:*         {p4_stat}\n"
                f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
                f"{current['detail']}\n\n"
                f"`[{gauge}]`  *{current['progress']}%*\n\n"
                f"⏳ Fetching custom news{topic_str}. Just a moment!"
            )
            await message.edit_text(text=text, parse_mode="Markdown")
            idx += 1
        except asyncio.CancelledError:
            break
        except Exception:
            pass


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline keyboard button clicks."""
    query = update.callback_query
    await query.answer()
    
    chat_id = query.message.chat_id
    action = query.data
    
    if action == "latest":
        chat_id = query.message.chat_id
        
        keyboard = [
            [
                InlineKeyboardButton("📰 Get Latest Digest", callback_data="latest"),
                InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        cached_file_id = await database.get_cached_file_id_exact("latest")
        if cached_file_id:
            caption = f"📰 *{BRAND_NAME}* | Here is your daily newsletter!\n\nEnjoy reading!"
            try:
                await context.bot.send_document(chat_id=chat_id, document=cached_file_id, caption=caption, parse_mode="Markdown", reply_markup=reply_markup)
                try:
                    await query.message.delete()
                except Exception as e:
                    logger.debug(f"Could not delete query message: {e}")
                return
            except Exception as e:
                logger.warning(f"Failed to send cached file_id, generating fresh: {e}")
                
        loading_msg = await query.edit_message_text(text="⏳ Connecting to news sources... Just a moment!")
        
        # Start dynamic progress updates in the background
        ticker_task = asyncio.create_task(update_loading_message(loading_msg, context))
        
        pdf_filename = None
        try:
            # Run the synchronous digest generation in a thread
            pdf_filename = await asyncio.to_thread(generate_latest_digest, 5)
        finally:
            ticker_task.cancel()
            try:
                await ticker_task
            except asyncio.CancelledError:
                pass
            try:
                await loading_msg.delete()
            except Exception as e:
                logger.error(f"Failed to delete temporary loading message: {e}")
            
        if pdf_filename and os.path.exists(pdf_filename):
            try:
                caption = f"📰 *{BRAND_NAME}* | Here is your daily newsletter!\n\nEnjoy reading!"
                pretty_filename = os.path.basename(pdf_filename).replace("_", " ")
                with open(pdf_filename, "rb") as file:
                    msg = await context.bot.send_document(chat_id=chat_id, document=file, filename=pretty_filename, caption=caption, parse_mode="Markdown", reply_markup=reply_markup)
                    if msg and msg.document:
                        await database.set_cached_file_id_exact("latest", msg.document.file_id)
            finally:
                try:
                    os.remove(pdf_filename)
                except Exception as e:
                    logger.error(f"Failed to delete {pdf_filename}: {e}")
        else:
            back_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]])
            await context.bot.send_message(chat_id=chat_id, text="❌ Sorry, I had some trouble generating the newsletter. Please try again in a few minutes!", reply_markup=back_keyboard)
            
    elif action == "subscribe":
        added = await database.add_subscriber(chat_id)
        back_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]])
        if added:
            await query.edit_message_text(text="✅ Subscribed successfully! You will now receive daily news updates automatically.", reply_markup=back_keyboard)
        else:
            await query.edit_message_text(text="ℹ️ You are already subscribed to daily updates.", reply_markup=back_keyboard)
            
    elif action == "unsubscribe":
        removed = await database.remove_subscriber(chat_id)
        back_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]])
        if removed:
            await query.edit_message_text(text="🔕 Unsubscribed successfully. You will no longer receive daily updates.", reply_markup=back_keyboard)
        else:
            await query.edit_message_text(text="ℹ️ You are not currently subscribed to daily updates.", reply_markup=back_keyboard)
            
    elif action == "about":
        about_text = (
            f"✨ *About {BRAND_NAME}*\n\n"
            f"This bot is powered by smart AI. It automatically searches for major news stories, "
            f"rewrites them to be quick and easy to read, and designs a premium PDF newsletter "
            f"just for you.\n\n"
            f"Designed & Built with ❤️ by Sumanth."
        )
        back_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]])
        await query.edit_message_text(text=about_text, reply_markup=back_keyboard, parse_mode="Markdown")
        
    elif action == "main_menu":
        first_name = query.from_user.first_name or "Reader"
        welcome_text, reply_markup = get_main_menu(first_name)
        await query.edit_message_text(text=welcome_text, reply_markup=reply_markup, parse_mode="Markdown")
        
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
            await query.edit_message_text(text=stats_text, reply_markup=reply_markup, parse_mode="Markdown")
            
        elif action == "admin_broadcast":
            loading_msg = await query.edit_message_text(text="⏳ Preparing global broadcast. Please standby...")
            ticker_task = asyncio.create_task(update_loading_message(loading_msg, context))
            try:
                await scheduled_broadcast(context, force_fresh=True)
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
            keyboard = [
                [
                    InlineKeyboardButton("📊 View Stats", callback_data="admin_stats"),
                    InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            await context.bot.send_message(chat_id=chat_id, text="✅ Global broadcast completed successfully!", reply_markup=reply_markup, parse_mode="Markdown")

async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /news command to fetch targeted news using semantic matching."""
    query = " ".join(context.args)
    chat_id = update.message.chat_id
    
    if not query:
        back_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]])
        await update.message.reply_text("Please specify a topic! Example: `/news space exploration`", reply_markup=back_keyboard, parse_mode="Markdown")
        return
        
    cached_file_id = await database.get_cached_file_id_semantic(query)
    if cached_file_id:
        caption = f"✅ Search finished! Sending your newsletter about *{query}*..."
        keyboard = [
            [
                InlineKeyboardButton("📰 Get Latest Digest", callback_data="latest"),
                InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        try:
            await context.bot.send_document(chat_id=chat_id, document=cached_file_id, caption=caption, parse_mode="Markdown", reply_markup=reply_markup)
            return
        except Exception as e:
            logger.warning(f"Failed to send cached targeted file_id, generating fresh: {e}")
            
    loading_msg = await update.message.reply_text(f"⏳ Connecting to news sources... Just a moment!", parse_mode="Markdown")
    
    # Start dynamic progress updates in the background
    ticker_task = asyncio.create_task(update_loading_message(loading_msg, context, topic=query))
    
    try:
        pdf_filename = await asyncio.to_thread(generate_targeted_digest, query, 5)
    finally:
        # Cancel the progress ticker
        ticker_task.cancel()
        try:
            await ticker_task
        except asyncio.CancelledError:
            pass
        # Delete the temporary loading message
        try:
            await loading_msg.delete()
        except Exception as e:
            logger.error(f"Failed to delete temporary loading message: {e}")
    
    if pdf_filename and os.path.exists(pdf_filename):
        try:
            caption = f"✅ Search finished! Sending your newsletter about *{query}*..."
            pretty_filename = os.path.basename(pdf_filename).replace("_", " ")
            keyboard = [
                [
                    InlineKeyboardButton("📰 Get Latest Digest", callback_data="latest"),
                    InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
                ]
            ]
            reply_markup = InlineKeyboardMarkup(keyboard)
            with open(pdf_filename, "rb") as file:
                msg = await context.bot.send_document(chat_id=chat_id, document=file, filename=pretty_filename, caption=caption, parse_mode="Markdown", reply_markup=reply_markup)
                if msg and msg.document:
                    await database.set_cached_file_id_semantic(query, msg.document.file_id)
        finally:
            try:
                os.remove(pdf_filename)
            except Exception as e:
                logger.error(f"Failed to delete {pdf_filename}: {e}")
    else:
        back_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]])
        await context.bot.send_message(chat_id=chat_id, text=f"😔 Sorry, I couldn't find enough news about *{query}* right now. Try another topic!", reply_markup=back_keyboard, parse_mode="Markdown")

@admin_only
async def admin_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /admin_stats command."""
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
    await update.message.reply_text(stats_text, reply_markup=reply_markup, parse_mode="Markdown")

@admin_only
async def admin_broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Force an immediate daily broadcast (Admin Only)."""
    loading_msg = await update.message.reply_text("⏳ Preparing global broadcast. Please standby...")
    ticker_task = asyncio.create_task(update_loading_message(loading_msg, context))
    try:
        await scheduled_broadcast(context, force_fresh=True)
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
            
    keyboard = [
        [
            InlineKeyboardButton("📊 View Stats", callback_data="admin_stats"),
            InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text("✅ Global broadcast completed successfully!", reply_markup=reply_markup, parse_mode="Markdown")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command with context-specific inline keyboard."""
    user_id = str(update.effective_user.id) if update.effective_user else ""
    admin_id = os.getenv("ADMIN_ID", "6038057345")
    is_admin = user_id == admin_id
    
    help_text = (
        f"📖 *{BRAND_NAME}* | Help Menu\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🤖 *General Commands:*\n"
        f"• `/start` - Open the main menu.\n"
        f"• `/news <topic>` - Get news about a specific topic (e.g., `/news solar energy`).\n"
        f"• `/help` - Show this help guide.\n\n"
    )
    
    if is_admin:
        help_text += (
            f"⚙️ *Admin Commands:*\n"
            f"• `/status` - Check if the database and system are online.\n"
            f"• `/stats` - View total subscriber count.\n"
            f"• `/broadcast` - Send out today's newsletter to all subscribers.\n\n"
        )
        
    help_text += (
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"If you have any questions or feedback, contact @Sumanth."
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
        f"🖥️ *{BRAND_NAME}* | System Status\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"⚙️ *Database*: {db_status}\n"
        f"👤 *Your Subscription*: {sub_status}\n"
        f"🕒 *Server Time*: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')} UTC\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━"
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
        "I am a news bot! Use /start to see the menu, or use `/news <topic>` to fetch news about a specific topic.\n\n"
        "Example: `/news smartphone price hikes`"
    )
    back_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]])
    await update.message.reply_text(text, reply_markup=back_keyboard, parse_mode="Markdown")

async def scheduled_broadcast(context: ContextTypes.DEFAULT_TYPE, force_fresh: bool = False) -> None:
    """Scheduled job to generate the daily digest and send it to all subscribers."""
    logger.info("Starting scheduled daily broadcast...")
    
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
        return
        
    cached_file_id = None if force_fresh else await database.get_cached_file_id_exact("latest")
    pdf_filename = None
    
    if cached_file_id:
        logger.info("Using cached latest digest for scheduled broadcast.")
    else:
        pdf_filename = await asyncio.to_thread(generate_latest_digest, 5)  # Cap at 5 for the single page layout
        if not pdf_filename or not os.path.exists(pdf_filename):
            logger.error("Failed to generate PDF for broadcast.")
            return
            
    caption = f"📰 *{BRAND_NAME}* | Digest for {datetime.now().strftime('%b %d, %Y')}\n\nInnovating the future, today."
    
    success_count = 0
    if pdf_filename:
        pretty_filename = os.path.basename(pdf_filename).replace("_", " ")
        
    for chat_id in subscribers:
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
        except Forbidden:
            logger.warning(f"User {chat_id} blocked the bot. Removing subscriber.")
            await database.remove_subscriber(chat_id)
        except BadRequest as e:
            if "chat not found" in str(e).lower():
                logger.warning(f"Chat {chat_id} not found. Removing subscriber.")
                await database.remove_subscriber(chat_id)
            else:
                logger.error(f"Failed to send to {chat_id} (BadRequest): {e}")
        except Exception as e:
            logger.error(f"Failed to send to {chat_id}: {e}")
            
    logger.info(f"Broadcast completed. Sent to {success_count}/{len(subscribers)} subscribers.")
    
    if pdf_filename:
        try:
            os.remove(pdf_filename)
        except Exception as e:
            logger.error(f"Failed to clean up broadcast PDF {pdf_filename}: {e}")

async def ping_handler(request):
    return web.Response(text="OK")

async def start_web_server():
    port = int(os.getenv("PORT", 8080))
    web_app = web.Application()
    web_app.router.add_get('/ping', ping_handler)
    web_app.router.add_get('/', ping_handler)
    
    runner = web.AppRunner(web_app)
    await runner.setup()
    site = web.TCPSite(runner, '0.0.0.0', port)
    await site.start()
    logger.info(f"Dummy web server started on port {port}")
    return runner

async def post_init(app: Application) -> None:
    """Initialize the database during bot startup."""
    await database.init_db()
    app.bot_data['web_runner'] = await start_web_server()
    
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
                    BotCommand("broadcast", "📢 Force immediate broadcast")
                ]
                success = await app.bot.set_my_commands(admin_commands, scope=BotCommandScopeChat(chat_id=admin_chat_id))
                logger.info(f"Telegram set_my_commands API response: {success}")
                
                # Verify registration
                registered = await app.bot.get_my_commands(scope=BotCommandScopeChat(chat_id=admin_chat_id))
                logger.info(f"Verified registered commands for admin {admin_chat_id}: {[cmd.command for cmd in registered]}")
            except ValueError:
                logger.warning(f"Invalid ADMIN_ID format: {admin_id}")
    except Exception as e:
        logger.error(f"Failed to register admin-scoped commands with Telegram: {e}")

async def post_stop(app: Application) -> None:
    """Gracefully close external resources."""
    runner = app.bot_data.get('web_runner')
    if runner:
        await runner.cleanup()
        logger.info("Web server cleanly terminated.")
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
        .build()
    )
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("news", news_command))
    app.add_handler(CommandHandler("status", status_command))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("broadcast", admin_broadcast_command))
    app.add_handler(CommandHandler("stats", admin_stats_command))
    app.add_handler(CommandHandler("admin_stats", admin_stats_command))
    app.add_handler(CommandHandler("admin_broadcast", admin_broadcast_command))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, general_message_handler))
    
    # Schedule the daily broadcast at 10:00 AM IST (Asia/Kolkata)
    # Using python-telegram-bot's built-in job queue
    job_queue = app.job_queue
    ist_tz = pytz.timezone('Asia/Kolkata')
    broadcast_time = time(hour=10, minute=0, tzinfo=ist_tz)
    job_queue.run_daily(scheduled_broadcast, broadcast_time)
    
    return app

if __name__ == "__main__":
    app = build_bot()
    logger.info("Bot is starting... Press Ctrl+C to stop.")
    app.run_polling()

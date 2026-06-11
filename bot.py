import os
import asyncio
import logging
from datetime import time, datetime
import pytz
from dotenv import load_dotenv
from functools import wraps
from aiohttp import web

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, BotCommand, BotCommandScopeChat
from telegram.ext import Application, ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.error import Forbidden, BadRequest

def admin_only(func):
    @wraps(func)
    async def wrapper(update: Update, context: ContextTypes.DEFAULT_TYPE, *args, **kwargs):
        user_id = str(update.effective_user.id)
        admin_id = os.getenv("ADMIN_ID", "6038057345")
        if user_id != admin_id:
            await update.message.reply_text("⛔ Unauthorized. Admin access only.")
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

load_dotenv()
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Application is used directly to support Python 3.11+ compatibility.

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message with an inline keyboard."""
    first_name = update.effective_user.first_name or "Reader"
    welcome_text = (
        f"🚀 *{BRAND_NAME.upper()}* | Autonomous Intelligence\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"👋 *Welcome, {first_name}!* \n\n"
        f"I am your autonomous tech journalism agent. I curate key global developments, "
        f"synthesize insights using advanced AI models, and deliver a premium, "
        f"highly-structured PDF digest directly to you.\n\n"
        f"💡 *Key Coverage Areas:*\n"
        f"• 🧠 *Artificial Intelligence* & deep learning breakthroughs.\n"
        f"• 🔒 *Cybersecurity* threats & defense protocols.\n"
        f"• 🌐 *Infrastructure* & scalable cloud systems.\n"
        f"• 📈 *Macro Tech Trends* & VC landscape.\n\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"⚡ *Choose an option below to interact:*"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("📰 Get Latest Digest", callback_data="latest"),
            InlineKeyboardButton("ℹ️ Project About", callback_data="about")
        ],
        [
            InlineKeyboardButton("🔔 Subscribe Daily", callback_data="subscribe"),
            InlineKeyboardButton("🔕 Unsubscribe", callback_data="unsubscribe")
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(welcome_text, reply_markup=reply_markup, parse_mode="Markdown")

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle inline keyboard button clicks."""
    query = update.callback_query
    await query.answer()
    
    chat_id = query.message.chat_id
    action = query.data
    
    if action == "latest":
        await query.edit_message_text(text="⏳ Generating the latest digest... Please wait, this might take a few minutes.")
        
        # Run the synchronous digest generation in a thread
        pdf_filename = await asyncio.to_thread(generate_latest_digest, 5)
        
        if pdf_filename and os.path.exists(pdf_filename):
            try:
                caption = f"📰 *{BRAND_NAME}* | Here is the latest digest!\n\nInnovating the future, today."
                pretty_filename = os.path.basename(pdf_filename).replace("_", " ")
                with open(pdf_filename, "rb") as file:
                    await context.bot.send_document(chat_id=chat_id, document=file, filename=pretty_filename, caption=caption, parse_mode="Markdown")
                await query.message.reply_text("✅ Delivered!")
            finally:
                try:
                    os.remove(pdf_filename)
                except Exception as e:
                    logger.error(f"Failed to delete {pdf_filename}: {e}")
        else:
            await query.message.reply_text("❌ Failed to generate the digest. Please try again later.")
            
    elif action == "subscribe":
        added = await database.add_subscriber(chat_id)
        if added:
            await query.edit_message_text(text="✅ You have successfully subscribed! You will receive the daily tech digest automatically.")
        else:
            await query.edit_message_text(text="ℹ️ You are already subscribed.")
            
    elif action == "unsubscribe":
        removed = await database.remove_subscriber(chat_id)
        if removed:
            await query.edit_message_text(text="🔕 You have unsubscribed. You will no longer receive daily digests.")
        else:
            await query.edit_message_text(text="ℹ️ You are not currently subscribed.")
            
    elif action == "about":
        about_text = (
            f"🤖 *About {BRAND_NAME}*\n\n"
            f"This bot is a fully autonomous AI-powered pipeline. It aggregates top tech news, "
            f"uses advanced LLMs (like Nemotron & Gemma) to structure it, and renders a stunning "
            f"PDF magazine entirely from scratch.\n\n"
            f"Curated & Engineered by Sumanth."
        )
        await query.edit_message_text(text=about_text, parse_mode="Markdown")

async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /news command to fetch targeted news."""
    query = " ".join(context.args) if context.args else ""
    chat_id = update.message.chat_id
    
    if not query:
        await update.message.reply_text("Please provide a topic. Example: `/news cybersecurity`", parse_mode="Markdown")
        return
        
    await update.message.reply_text(f"⏳ Executing deepdive protocol for: *{query}*. Searching across global feeds...", parse_mode="Markdown")
    
    pdf_filename = await asyncio.to_thread(generate_targeted_digest, query, 5)
    
    if pdf_filename and os.path.exists(pdf_filename):
        try:
            caption = f"✅ Deepdive complete. Delivering payload for *{query}*..."
            pretty_filename = os.path.basename(pdf_filename).replace("_", " ")
            with open(pdf_filename, "rb") as file:
                await context.bot.send_document(chat_id=chat_id, document=file, filename=pretty_filename, caption=caption, parse_mode="Markdown")
        finally:
            try:
                os.remove(pdf_filename)
            except Exception as e:
                logger.error(f"Failed to delete {pdf_filename}: {e}")
    else:
        await update.message.reply_text(f"❌ Failed to find enough news or generate the digest for *{query}*.")

@admin_only
async def admin_stats_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /admin_stats command."""
    subscribers = await database.get_all_subscribers()
    stats_text = (
        f"📊 *Admin Statistics*\n\n"
        f"👥 Total Subscribers: {len(subscribers)}\n"
        f"🕒 Server Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
    )
    await update.message.reply_text(stats_text, parse_mode="Markdown")

@admin_only
async def admin_broadcast_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /admin_broadcast command."""
    await update.message.reply_text("⏳ Forcing a global broadcast now. Please wait...")
    # Run the scheduled broadcast immediately
    await scheduled_broadcast(context)
    await update.message.reply_text("✅ Global broadcast completed!")

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /help command."""
    help_text = (
        f"📖 *{BRAND_NAME}* | Help Menu\n"
        f"━━━━━━━━━━━━━━━━━━━━━━\n\n"
        f"🤖 *General Commands:*\n"
        f"• `/start` - Greet and show main menu.\n"
        f"• `/news <topic>` - Fetch a targeted news digest (e.g., `/news AI`).\n"
        f"• `/status` - Check database & subscription status.\n"
        f"• `/help` - Show this help message.\n\n"
    )
    
    # Check if the user is the admin
    user_id = str(update.effective_user.id)
    admin_id = os.getenv("ADMIN_ID", "6038057345")
    if user_id == admin_id:
        help_text += (
            f"⚙️ *Admin Commands:*\n"
            f"• `/stats` - View subscriber stats.\n"
            f"• `/broadcast` - Trigger immediate global broadcast.\n\n"
        )
        
    help_text += (
        f"━━━━━━━━━━━━━━━━━━━━━━\n"
        f"If you have any questions or feedback, contact @Sumanth."
    )
    await update.message.reply_text(help_text, parse_mode="Markdown")

async def status_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle the /status command."""
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
    await update.message.reply_text(status_text, parse_mode="Markdown")

async def general_message_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handle all other text messages."""
    text = (
        "I am a news bot! Use /start to see the menu, or use `/news <topic>` to fetch news about a specific topic.\n\n"
        "Example: `/news smartphone price hikes`"
    )
    await update.message.reply_text(text, parse_mode="Markdown")

async def scheduled_broadcast(context: ContextTypes.DEFAULT_TYPE) -> None:
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
        
    pdf_filename = await asyncio.to_thread(generate_latest_digest, 5)  # Cap at 5 for the single page layout
    
    if not pdf_filename or not os.path.exists(pdf_filename):
        logger.error("Broadcast failed: Could not generate digest.")
        return
        
    caption = f"📰 *{BRAND_NAME}* | Digest for {datetime.now().strftime('%b %d, %Y')}\n\nInnovating the future, today."
    
    success_count = 0
    pretty_filename = os.path.basename(pdf_filename).replace("_", " ")
    file_id = None
    for chat_id in subscribers:
        try:
            if file_id:
                await context.bot.send_document(chat_id=chat_id, document=file_id, caption=caption, parse_mode="Markdown")
            else:
                with open(pdf_filename, "rb") as file:
                    msg = await context.bot.send_document(chat_id=chat_id, document=file, filename=pretty_filename, caption=caption, parse_mode="Markdown")
                    if msg and msg.document:
                        file_id = msg.document.file_id
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

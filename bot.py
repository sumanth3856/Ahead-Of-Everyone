import os
import asyncio
import logging
from datetime import time, datetime
import pytz
from dotenv import load_dotenv
from functools import wraps

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, ApplicationBuilder, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

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

class SubApplication(Application):
    """Subclass of Application to explicitly support weak references in Python 3.13."""
    __slots__ = ('__weakref__',)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send a welcome message with an inline keyboard."""
    welcome_text = (
        f"👋 Welcome to *{BRAND_NAME}*!\n\n"
        f"I am your autonomous tech journalism bot. I scrape the global tech news, "
        f"structure it with AI, and deliver a premium PDF magazine straight to you.\n\n"
        f"What would you like to do?"
    )
    
    keyboard = [
        [
            InlineKeyboardButton("📰 Latest Digest", callback_data="latest"),
            InlineKeyboardButton("ℹ️ About", callback_data="about")
        ],
        [
            InlineKeyboardButton("🔔 Subscribe", callback_data="subscribe"),
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
            caption = f"📰 *{BRAND_NAME}* | Here is the latest digest!\n\nInnovating the future, today."
            pretty_filename = os.path.basename(pdf_filename).replace("_", " ")
            with open(pdf_filename, "rb") as file:
                await context.bot.send_document(chat_id=chat_id, document=file, filename=pretty_filename, caption=caption, parse_mode="Markdown")
            await query.message.reply_text("✅ Delivered!")
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
        caption = f"✅ Deepdive complete. Delivering payload for *{query}*..."
        pretty_filename = os.path.basename(pdf_filename).replace("_", " ")
        with open(pdf_filename, "rb") as file:
            await context.bot.send_document(chat_id=chat_id, document=file, filename=pretty_filename, caption=caption, parse_mode="Markdown")
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
    pdf_filename = await asyncio.to_thread(generate_latest_digest, 5)  # Cap at 5 for the single page layout
    
    if not pdf_filename or not os.path.exists(pdf_filename):
        logger.error("Broadcast failed: Could not generate digest.")
        return
        
    subscribers = await database.get_all_subscribers()
    if not subscribers:
        logger.info("No subscribers found for broadcast.")
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
        except Exception as e:
            logger.error(f"Failed to send to {chat_id}: {e}")
            
    logger.info(f"Broadcast completed. Sent to {success_count}/{len(subscribers)} subscribers.")

async def post_init(app: Application) -> None:
    """Initialize the database during bot startup."""
    await database.init_db()

def build_bot() -> Application:
    """Build the bot application."""
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set in environment variables!")
        exit(1)
        
    app = (
        ApplicationBuilder()
        .token(BOT_TOKEN)
        .application_class(SubApplication)
        .post_init(post_init)
        .build()
    )
    
    app.add_handler(CommandHandler("start", start_command))
    app.add_handler(CommandHandler("news", news_command))
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

import os
import logging
import asyncio
import nest_asyncio
from dotenv import load_dotenv
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

import config
from scraper import fetch_dynamic_news, fetch_targeted_news, register_sent_stories
from pdf_generator import generate_digest_pdf

# Allow nested asyncio loops for environments that might need it
nest_asyncio.apply()

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Send a message when the command /start is issued."""
    welcome_text = (
        "🚀 *Welcome to Ahead of Everyone (AoE) - Interactive Mode*\n\n"
        "I am your elite AI tech journalist. I don't just scrape the news, I analyze and structure it into a premium dark-mode magazine.\n\n"
        "*Commands:*\n"
        "📰 `/daily` - Manually trigger the massive daily pulse (Top 5-7 stories of the last 24h).\n"
        "🎯 `/news [topic]` - E.g. `/news crypto` or `/news apple`. Generates a custom deepdive on the fly."
    )
    await update.message.reply_text(welcome_text, parse_mode="Markdown")

async def daily_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generates the standard daily digest and registers it."""
    chat_id = update.effective_chat.id
    await update.message.reply_text("⏳ Scraping, filtering rehashes, and analyzing the last 24 hours of tech news. This will take ~1-2 minutes...")
    
    try:
        # Run synchronous fetching in a thread to not block the async loop
        loop = asyncio.get_running_loop()
        stories = await loop.run_in_executor(None, fetch_dynamic_news, 7)
        
        if not stories:
            await update.message.reply_text("⚠️ No new stories found that haven't already been covered recently.")
            return
            
        pdf_filename = await loop.run_in_executor(None, generate_digest_pdf, stories, None)
        
        if not pdf_filename or not os.path.exists(pdf_filename):
            await update.message.reply_text("❌ Failed to generate the PDF magazine.")
            return
            
        # Send the PDF document
        await update.message.reply_text("✅ Magazine generated successfully. Delivering payload...")
        with open(pdf_filename, 'rb') as doc:
            await context.bot.send_document(chat_id=chat_id, document=doc)
            
        # Register stories so they aren't repeated
        await loop.run_in_executor(None, register_sent_stories, stories)
        
    except Exception as e:
        logger.error(f"Error in /daily command: {e}")
        await update.message.reply_text("❌ An error occurred during pipeline execution.")

async def news_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Generates a custom, on-demand digest for a specific topic."""
    chat_id = update.effective_chat.id
    
    if not context.args:
        await update.message.reply_text("⚠️ Please provide a topic. Example: `/news artificial intelligence`", parse_mode="Markdown")
        return
        
    topic = " ".join(context.args)
    await update.message.reply_text(f"⏳ Executing deepdive protocol for: *{topic}*. Searching across global feeds...", parse_mode="Markdown")
    
    try:
        loop = asyncio.get_running_loop()
        stories = await loop.run_in_executor(None, fetch_targeted_news, topic, 5)
        
        if not stories:
            await update.message.reply_text(f"⚠️ Could not find enough recent news for '{topic}'.")
            return
            
        pdf_filename = await loop.run_in_executor(None, generate_digest_pdf, stories, topic)
        
        if not pdf_filename or not os.path.exists(pdf_filename):
            await update.message.reply_text("❌ Failed to generate the PDF magazine.")
            return
            
        await update.message.reply_text(f"✅ Deepdive complete. Delivering payload for *{topic}*...", parse_mode="Markdown")
        with open(pdf_filename, 'rb') as doc:
            await context.bot.send_document(chat_id=chat_id, document=doc)
            
        # We do NOT register on-demand stories. They bypass the anti-rehash filter.
        
    except Exception as e:
        logger.error(f"Error in /news command: {e}")
        await update.message.reply_text("❌ An error occurred during targeted execution.")

def main():
    """Start the bot."""
    load_dotenv()
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN is not set.")
        return

    # Create the Application and pass it your bot's token. Disable job_queue to avoid weakref issues in Python 3.13
    application = Application.builder().token(token).job_queue(None).build()

    # on different commands - answer in Telegram
    application.add_handler(CommandHandler("start", start_command))
    application.add_handler(CommandHandler("daily", daily_command))
    application.add_handler(CommandHandler("news", news_command))
    application.add_handler(CommandHandler("deepdive", news_command)) # Alias

    logger.info("AoE Interactive Bot is starting... Polling for messages 24/7.")
    
    # Run the bot until the user presses Ctrl-C
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

import asyncio
from datetime import datetime
import pytz
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

def get_back_keyboard():
    keyboard = [[InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")]]
    return InlineKeyboardMarkup(keyboard)

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

def get_about_menu(is_subscribed: bool = False):
    about_text = (
        f"*[ ABOUT THIS BOT ]*\n\n"
        f"This bot is powered by smart AI. It automatically searches for major news stories, rewrites them to be quick and easy to read, and designs a premium PDF newsletter just for you."
    )
    keyboard = [[InlineKeyboardButton("📰 Get Latest Digest", callback_data="latest")]]
    if is_subscribed:
        keyboard.append([InlineKeyboardButton("🔕 Stop Daily Digests", callback_data="unsubscribe")])
    else:
        keyboard.append([InlineKeyboardButton("🔔 Get Daily Digests", callback_data="subscribe")])
    keyboard.append([InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")])
    
    return about_text, InlineKeyboardMarkup(keyboard)

def get_stats_menu(subscribers_count: int):
    stats_text = (
        f"📊 *Admin Statistics*\n\n"
        f"👥 Total Subscribers: {subscribers_count}\n"
        f"⏱️ Server Time: {datetime.now(pytz.timezone('Asia/Kolkata')).strftime('%Y-%m-%d %H:%M:%S')} IST"
    )
    keyboard = [
        [
            InlineKeyboardButton("📢 Broadcast Now", callback_data="admin_broadcast"),
            InlineKeyboardButton("🔙 Back to Main Menu", callback_data="main_menu")
        ]
    ]
    return stats_text, InlineKeyboardMarkup(keyboard)

async def update_loading_message(message, bot, progress_state, topic=None) -> None:
    """Periodically update the loading message based on the real-time progress state from the backend logic."""
    topic_str = f" about *{topic}*" if topic else ""
    chat_id = message.chat_id
    
    # Animated emojis that cycle on each update to show the bot is alive
    ticker_emojis = ["🔄", "⏳", "✨", "⚙️", "🚀", "⚡", "🛰️", "🤖", "📡", "💡"]
    fun_facts = [
        "Did you know? The first computer bug was an actual moth found in 1947. 🐛",
        "Hang tight! Our 120-Billion parameter AI is reading the news faster than a caffeinated squirrel. 🐿️☕",
        "Fun fact: 90% of the world's data was generated in the last two years alone! 📈",
        "Just a moment... The AI is doing some heavy mental lifting. 🏋️‍♂️🤖",
        "Did you know? The Apollo 11 computer had less memory than a modern smart bulb. 💡🚀",
        "Almost there! Compiling a Pulitzer-level intelligence briefing just for you. 📰✨",
        "Fun fact: The first domain ever registered was Symbolics.com in 1985. 🌐",
        "Wait for it... Our digital journalists are putting on the finishing touches! 🧑‍💻✍️"
    ]
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
            
            # Phase statuses synchronized with actual pipeline progression
            p1_stat = "✅ Sourced" if "Finding Stories" in done_phases else (f"{tick_emoji} Scouting..." if phase == "Finding Stories" else "⏳ Waiting")
            p2_stat = "✅ Synthesized" if "Writing Summaries" in done_phases else (f"{tick_emoji} Deep Thinking..." if phase == "Writing Summaries" else "⏳ Waiting")
            p3_stat = "✅ Crafted" if "Creating PDF" in done_phases else (f"{tick_emoji} Designing..." if phase == "Creating PDF" else "⏳ Waiting")
            p4_stat = "✅ Dispatched" if "Delivering" in done_phases else (f"{tick_emoji} Preparing..." if phase == "Delivering" else "⏳ Waiting")
            
            filled_length = int(progress / 5)
            gauge = "█" * filled_length + "░" * (20 - filled_length)
            
            loading_text = (
                f"🚀 *GENERATING AI NEWSLETTER*{topic_str}\n\n"
                f"*{phase}*\n"
                f"[{gauge}] {progress}%\n\n"
                f"*{p1_stat}* | Finding high-signal stories\n"
                f"*{p2_stat}* | AI distilling content to 80%\n"
                f"*{p3_stat}* | Rendering premium document\n"
                f"*{p4_stat}* | Sending to your device\n\n"
                f"_{detail}_\n\n"
                f"💡 {fun_facts[idx % len(fun_facts)]}"
            )
            
            # Use specific cancel callback for query vs latest
            cancel_data = f"cancel_query" if topic else "cancel_latest"
            cancel_keyboard = InlineKeyboardMarkup([[InlineKeyboardButton("🛑 Cancel Generation", callback_data=cancel_data)]])
            
            await message.edit_text(loading_text, parse_mode="Markdown", reply_markup=cancel_keyboard)
            
        except Exception:
            pass
            
        idx += 1
        await asyncio.sleep(2.5)

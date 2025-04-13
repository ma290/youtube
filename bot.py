import logging
import os
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,  # Changed from Filters to filters
    ContextTypes,
)
import yt_dlp

# Enable logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot token hardcoded (replace with your actual token)
TOKEN = "your-bot-token-here"  # Replace with your BotFather token

# Define the /start command handler
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "Hello! I'm a YouTube downloader bot. Send me a YouTube link, and I'll download it in the best format!"
    )

# Define the handler for YouTube links
async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    url = update.message.text
    chat_id = update.effective_chat.id

    # Validate URL
    if "youtube.com" not in url and "youtu.be" not in url:
        await context.bot.send_message(
            chat_id=chat_id, text="Please send a valid YouTube URL."
        )
        return

    await context.bot.send_message(chat_id=chat_id, text="Processing your request...")

    # yt-dlp options for best format (prefer MP4, merge video+audio)
    ydl_opts = {
        "format": "bestvideo[ext=mp4]+bestaudio[ext=m4a]/best[ext=mp4]/best",
        "outtmpl": "downloaded_video.%(ext)s",  # Output filename
        "merge_output_format": "mp4",
        "quiet": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            # Download video
            info = ydl.extract_info(url, download=True)
            video_title = info.get("title", "video")
            video_file = "downloaded_video.mp4"

            # Check file size (Telegram limit: 50MB for bots)
            file_size = os.path.getsize(video_file) / (1024 * 1024)  # Size in MB
            if file_size > 50:
                await context.bot.send_message(
                    chat_id=chat_id,
                    text="Sorry, the video is too large (>50MB) for Telegram's free bot limit."
                )
                os.remove(video_file)  # Clean up
                return

            # Send video to user
            with open(video_file, "rb") as video:
                await context.bot.send_video(
                    chat_id=chat_id, video=video, caption=video_title
                )

            # Clean up downloaded file
            os.remove(video_file)

    except Exception as e:
        logger.error(f"Error downloading video: {e}")
        await context.bot.send_message(
            chat_id=chat_id, text="Failed to download the video. Try another link."
        )

# Main function to set up the bot
def main() -> None:
    if not TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN not set!")
        return

    # Create the Application
    application = Application.builder().token(TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))  # Updated Filters to filters

    # Start the bot
    application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == "__main__":
    main()

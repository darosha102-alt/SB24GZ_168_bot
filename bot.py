import os
import logging
import httpx
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.environ.get("BOT_TOKEN")

# Phone API configuration
# This example uses a public endpoint; please adjust according to actual API documentation
PHONE_API_URL = "https://api.example.com/v1/phones/latest"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        f"Hello! I am @SB24GZ_168_bot.\n"
        "I can display the latest phone series for you.\n\n"
        "Send /latest to get the latest phone list."
    )

async def latest_phones(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Fetch and display the latest phone series."""
    await update.message.reply_text("Fetching latest phone data, please wait...")

    try:
        async with httpx.AsyncClient(timeout=15.0) as client:
            resp = await client.get(PHONE_API_URL)
            resp.raise_for_status()
            data = resp.json()

        # Parse the response; the actual structure depends on the API documentation
        # Assume the response is a list, with each item containing name and release date
        phones = data if isinstance(data, list) else data.get("data", data.get("phones", []))

        if not phones:
            await update.message.reply_text("No phone data available at the moment.")
            return

        # Show the first 10 entries to avoid overly long messages
        lines = []
        for phone in phones[:10]:
            name = phone.get("name", phone.get("model", "Unknown model"))
            release = phone.get("release_date", phone.get("released", phone.get("year", "Unknown date")))
            lines.append(f"• {name} ({release})")

        reply = "📱 Latest Phone Series:\n\n" + "\n".join(lines)
        if len(phones) > 10:
            reply += f"\n\n...and {len(phones) - 10} more models."

        await update.message.reply_text(reply)

    except httpx.TimeoutException:
        logger.error("Phone API request timed out")
        await update.message.reply_text("⚠️ Request timed out, please try again later.")
    except httpx.HTTPStatusError as e:
        logger.error(f"Phone API HTTP error: {e}")
        await update.message.reply_text("⚠️ Phone data service is temporarily unavailable.")
    except Exception as e:
        logger.error(f"Phone API error: {e}")
        await update.message.reply_text("⚠️ Failed to fetch phone data, please try again later.")

def main():
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN environment variable not set!")
        return

    app = ApplicationBuilder().token(BOT_TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("latest", latest_phones))

    logger.info("Bot is starting...")
    app.run_polling()

if __name__ == '__main__':
    main()

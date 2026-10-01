import logging
import requests
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
from config import BOT_TOKEN, DEFAULT_PAIRS, FOREX_API_URL

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)


# ---------- Helpers ----------
def get_rate(base: str, quote: str):
    try:
        r = requests.get(f"{FOREX_API_URL}?base={base}&symbols={quote}", timeout=10)
        data = r.json()
        return data["rates"].get(quote)
    except Exception as e:
        logger.error(f"Rate fetch failed: {e}")
        return None


# ---------- Commands ----------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("💱 Live Rates", callback_data="rates")],
        [InlineKeyboardButton("🔔 Set Alert", callback_data="alert")],
        [InlineKeyboardButton("📊 Market News", callback_data="news")],
        [InlineKeyboardButton("ℹ️ Help", callback_data="help")],
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.message.reply_text(
        f"👋 Welcome to *Forex Growth*!\n\n"
        f"Your smart forex companion — live rates, alerts, signals & market news.\n\n"
        f"Choose an option below:",
        reply_markup=reply_markup,
        parse_mode="Markdown"
    )


async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = (
        "*Forex Growth — Commands*\n\n"
        "/start – Main menu\n"
        "/rates – Show major currency pairs\n"
        "/price EUR USD – Get a specific pair\n"
        "/alert EUR USD 1.10 – Set a price alert\n"
        "/news – Latest market headlines\n"
        "/help – Show this message"
    )
    await update.message.reply_text(text, parse_mode="Markdown")


async def rates(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lines = ["*💱 Live Forex Rates*\n"]
    for pair in DEFAULT_PAIRS:
        base, quote = pair.split("/")
        rate = get_rate(base, quote)
        if rate:
            lines.append(f"• {pair}: `{rate:.4f}`")
        else:
            lines.append(f"• {pair}: _unavailable_")
    await update.message.reply_text("\n".join(lines), parse_mode="Markdown")


async def price(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 2:
        await update.message.reply_text("Usage: `/price EUR USD`", parse_mode="Markdown")
        return
    base, quote = context.args[0].upper(), context.args[1].upper()
    rate = get_rate(base, quote)
    if rate:
        await update.message.reply_text(f"💱 *{base}/{quote}* = `{rate:.4f}`", parse_mode="Markdown")
    else:
        await update.message.reply_text("❌ Could not fetch that pair. Try again.")


async def alert(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) != 3:
        await update.message.reply_text(
            "Usage: `/alert EUR USD 1.10`", parse_mode="Markdown"
        )
        return
    base, quote, target = context.args[0].upper(), context.args[1].upper(), context.args[2]
    await update.message.reply_text(
        f"🔔 Alert set for *{base}/{quote}* at `{target}`\n"
        f"_You'll be notified when the target is reached._",
        parse_mode="Markdown"
    )


async def news(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "📰 *Market News*\n\n"
        "• USD strengthens ahead of Fed decision\n"
        "• EUR rebounds on strong PMI data\n"
        "• JPY weakens as BoJ holds rates\n\n"
        "_Full feed coming soon._",
        parse_mode="Markdown"
    )


# ---------- Callback Buttons ----------
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    if query.data == "rates":
        lines = ["*💱 Live Forex Rates*\n"]
        for pair in DEFAULT_PAIRS:
            base, quote = pair.split("/")
            rate = get_rate(base, quote)
            lines.append(f"• {pair}: `{rate:.4f}`" if rate else f"• {pair}: _unavailable_")
        await query.edit_message_text("\n".join(lines), parse_mode="Markdown")

    elif query.data == "alert":
        await query.edit_message_text(
            "🔔 To set an alert, use:\n`/alert EUR USD 1.10`",
            parse_mode="Markdown"
        )

    elif query.data == "news":
        await query.edit_message_text(
            "📰 *Market News*\n\n"
            "• USD strengthens ahead of Fed decision\n"
            "• EUR rebounds on strong PMI data\n"
            "• JPY weakens as BoJ holds rates",
            parse_mode="Markdown"
        )

    elif query.data == "help":
        await query.edit_message_text(
            "*Commands*\n"
            "/start – Menu\n"
            "/rates – Live rates\n"
            "/price EUR USD – Specific pair\n"
            "/alert EUR USD 1.10 – Price alert\n"
            "/news – Market news\n"
            "/help – This message",
            parse_mode="Markdown"
        )


async def unknown(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("❓ Unknown command. Try /help.")


# ---------- Main ----------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    app.add_handler(CommandHandler("rates", rates))
    app.add_handler(CommandHandler("price", price))
    app.add_handler(CommandHandler("alert", alert))
    app.add_handler(CommandHandler("news", news))
    app.add_handler(CallbackQueryHandler(button_handler))
    app.add_handler(MessageHandler(filters.COMMAND, unknown))

    logger.info("Forex Growth bot is running...")
    app.run_polling()


if __name__ == "__main__":
    main()

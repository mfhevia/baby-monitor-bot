from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
import requests
import os
from dotenv import load_dotenv

# Cargar variables del entorno
load_dotenv()

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
API_URL = os.getenv("API_URL")

allowed_ids = os.getenv("ALLOWED_USERS", "")
ALLOWED_USERS = set(int(uid.strip())
                    for uid in allowed_ids.split(",") if uid.strip().isdigit())

keyboard = [["💧 Pee", "💩 Poop", "💧+💩 Both"]]
reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Elige una opción:", reply_markup=reply_markup)


async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in ALLOWED_USERS:
        await update.message.reply_text('Unauthorized user.')
        return

    text = update.message.text

    payload = None
    if text == "💧 Pee":
        payload = {"type": "pee"}
    elif text == "💩 Poop":
        payload = {"type": "poop"}
    elif text == "💧+💩 Both":
        payload = {"type": "both"}

    if payload:
        try:
            response = requests.post(f'{API_URL}/diaper-changes', json=payload)
            data = response.json()
            await update.message.reply_text(f"API response: {data}", reply_markup=reply_markup)
        except Exception as e:
            await update.message.reply_text(f"Api error: {e}", reply_markup=reply_markup)
    else:
        await update.message.reply_text("Please push a button.", reply_markup=reply_markup)


def main():
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(
        filters.TEXT & ~filters.COMMAND, handle_message))
    app.run_polling()


if __name__ == "__main__":
    main()

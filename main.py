import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, ContextTypes, filters

# Логирование
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_IDS = os.getenv("ADMIN_CHAT_IDS", "").split(",")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Привет! Напиши мне сообщение, и я передам его администратору.")

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    message = update.message.text

    for admin_id in ADMIN_CHAT_IDS:
        try:
            await context.bot.send_message(chat_id=int(admin_id.strip()), text=f"📨 Новое сообщение от @{user.username or user.id}:

{message}")
        except Exception as e:
            logger.error(f"Ошибка при отправке админу: {e}")

    await update.message.reply_text("✅ Спасибо! Ваше сообщение получено.")

def main():
    if not TOKEN:
        raise ValueError("TELEGRAM_BOT_TOKEN не установлен!")
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    logger.info("🤖 Бот запущен...")
    app.run_polling()

if __name__ == "__main__":
    main()

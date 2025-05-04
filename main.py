import os
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes

# Получаем токен из переменных окружения
TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Получаем список ID админов из переменной окружения (через запятую)
ADMIN_CHAT_IDS = os.getenv("ADMIN_CHAT_IDS", "1559058125").split(",")

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Я бот обратной связи. Отправьте мне ваше сообщение, и я передам его администраторам."
    )

# Обработка любого текста
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    message = update.message.text

    # Ответ пользователю
    await update.message.reply_text(
        "✅ Спасибо за сообщение! Мы его передали администрации."
    )

    # Отправка сообщения администраторам
    for admin_id in ADMIN_CHAT_IDS:
        if admin_id.strip():
            await context.bot.send_message(
                chat_id=int(admin_id.strip()),
                text=f"📨 Новое сообщение от @{user.username or user.id}:\n\n{message}"
            )

def main():
    if not TOKEN:
        raise ValueError("❌ Ошибка: переменная окружения TELEGRAM_BOT_TOKEN не задана!")
    if not ADMIN_CHAT_IDS or ADMIN_CHAT_IDS == [""]:
        raise ValueError("❌ Ошибка: переменная окружения ADMIN_CHAT_IDS не задана!")

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    print("🤖 Бот запущен...")
    application.run_polling()

if __name__ == "__main__":
    main()

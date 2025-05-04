import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_IDS = os.getenv("ADMIN_CHAT_IDS", "1559058125").split(",")

# Храним временные данные о том, кому админ хочет ответить
pending_replies = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "Привет! Напиши сюда сообщение, и мы передадим его администрации."
    )

async def handle_user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.message.from_user
    message = update.message.text

    # Ответ пользователю
    await update.message.reply_text("✅ Спасибо! Ваше сообщение отправлено администрации.")

    # Кнопка "Ответить"
    reply_markup = InlineKeyboardMarkup([
        [InlineKeyboardButton("✉️ Ответить", callback_data=f"reply:{user.id}")]
    ])

    # Переслать сообщение администраторам
    for admin_id in ADMIN_CHAT_IDS:
        if admin_id.strip():
            await context.bot.send_message(
                chat_id=int(admin_id.strip()),
                text=f"📨 Сообщение от @{user.username or user.id}:\n\n{message}",
                reply_markup=reply_markup
            )

async def handle_reply_button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    data = query.data
    if data.startswith("reply:"):
        user_id = data.split(":")[1]
        admin_id = query.from_user.id
        pending_replies[admin_id] = user_id

        await query.message.reply_text("Введите сообщение, которое нужно отправить пользователю.")

async def handle_admin_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    admin_id = update.message.from_user.id
    text = update.message.text

    # Если админ нажал кнопку и теперь отправляет ответ
    if str(admin_id) in pending_replies:
        user_id = pending_replies[str(admin_id)]
        try:
            await context.bot.send_message(chat_id=int(user_id), text=f"📬 Ответ от администрации:\n\n{text}")
            await update.message.reply_text("✅ Сообщение отправлено.")
        except Exception as e:
            await update.message.reply_text(f"❌ Ошибка при отправке: {e}")
        del pending_replies[str(admin_id)]
    else:
        await update.message.reply_text("ℹ️ Сначала нажмите кнопку «Ответить» под сообщением пользователя.")

def main():
    if not TOKEN:
        raise ValueError("❌ Укажите TELEGRAM_BOT_TOKEN в переменных окружения")
    if not ADMIN_CHAT_IDS or ADMIN_CHAT_IDS == [""]:
        raise ValueError("❌ Укажите ADMIN_CHAT_IDS в переменных окружения")

    application = Application.builder().token(TOKEN).build()

    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_user_message))
    application.add_handler(CallbackQueryHandler(handle_reply_button))
    application.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, handle_admin_response))

    print("🤖 Бот запущен с кнопкой «Ответить»...")
    application.run_polling()

if __name__ == "__main__":
    main()

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
    ContextTypes,
    ConversationHandler
)
import sqlite3
import os

# Конфигурация
TOKEN = os.getenv("TELEGRAM_TOKEN")
ADMIN_ID = "1559058125"  # Ваш Telegram ID
DB_NAME = "feedback.db"

# Состояния для ConversationHandler
WAITING_RESPONSE = 1

# Настройка логгера
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Инициализация БД
def init_db():
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS messages
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  user_id INTEGER,
                  message TEXT,
                  response TEXT,
                  timestamp DATETIME DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

# Команда /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Здравствуйте! Напишите своё сообщение для АН BFS")

# Обработка сообщений от пользователей
async def user_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    text = update.message.text

    # Сохраняем сообщение в БД
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("INSERT INTO messages (user_id, message) VALUES (?, ?)", (user_id, text))
    conn.commit()
    conn.close()

    # Отправляем подтверждение пользователю
    await update.message.reply_text("📬 Ответ от АН BFS:\n✅ Ответ отправлен.")

    # Уведомление админу
    keyboard = [[InlineKeyboardButton("💬 Ответить", callback_data=f"reply_{user_id}")]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await context.bot.send_message(
        chat_id=ADMIN_ID,
        text=f"Новое сообщение от {user_id}:\n\n{text}",
        reply_markup=reply_markup
    )

# Обработка кнопки "Ответить"
async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    
    user_id = query.data.split("_")[1]
    context.user_data["reply_to"] = user_id
    
    await query.edit_message_text(
        text=f"️ Напишите ответ для chat_id: {user_id}"
    )
    return WAITING_RESPONSE

# Обработка ответа от админа
async def admin_response(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = context.user_data["reply_to"]
    admin_text = update.message.text

    # Сохраняем ответ в БД
    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("UPDATE messages SET response = ? WHERE user_id = ?", 
             (admin_text, user_id))
    conn.commit()
    conn.close()

    # Отправляем ответ пользователю
    await context.bot.send_message(
        chat_id=user_id,
        text=f"✅ Спасибо! Ваше сообщение передано.\n\nОтвет от АН BFS:\n{admin_text}"
    )

    # Подтверждение админу
    await update.message.reply_text("✅ Ответ успешно отправлен!")
    
    context.user_data.clear()
    return ConversationHandler.END

# Команда /admin для просмотра истории
async def admin(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if str(update.message.from_user.id) != ADMIN_ID:
        await update.message.reply_text("Доступ запрещен")
        return

    conn = sqlite3.connect(DB_NAME)
    c = conn.cursor()
    c.execute("SELECT * FROM messages ORDER BY timestamp DESC")
    messages = c.fetchall()
    conn.close()

    if not messages:
        await update.message.reply_text("Нет сообщений")
        return

    response = "История сообщений:\n\n"
    for msg in messages:
        response += f"ID: {msg[0]}\nUser: {msg[1]}\nСообщение: {msg[2]}\nОтвет: {msg[3]}\n\n"

    await update.message.reply_text(response)

def main():
    init_db()
    
    app = Application.builder().token(TOKEN).build()

    # ConversationHandler для ответов админа
    conv_handler = ConversationHandler(
        entry_points=[CallbackQueryHandler(button_handler, pattern="^reply_")],
        states={
            WAITING_RESPONSE: [MessageHandler(filters.TEXT & ~filters.COMMAND, admin_response)]
        },
        fallbacks=[]
    )

    # Регистрация обработчиков
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("admin", admin))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, user_message))
    app.add_handler(conv_handler)

    app.run_polling()

if __name__ == "__main__":
    main()

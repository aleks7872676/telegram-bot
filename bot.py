import os
import logging
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

# Настройка логов
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Конфигурация
BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
ADMIN_CHAT_IDS = [int(id) for id in os.getenv("ADMIN_IDS", "").split(",") if id]

if not BOT_TOKEN:
    logger.error("❌ TELEGRAM_BOT_TOKEN not set!")
    raise ValueError("Token not provided")

bot = telebot.TeleBot(BOT_TOKEN)
admin_reply_state = {}

@bot.message_handler(commands=["start"])
def start_handler(message):
    bot.send_message(message.chat.id, "👋 Здравствуйте! Напишите сообщение для АН BFS.")

@bot.message_handler(func=lambda m: True)
def handle_message(message):
    if message.chat.id in ADMIN_CHAT_IDS and message.chat.id in admin_reply_state:
        # Обработка ответа админа
        user_id = admin_reply_state.pop(message.chat.id)
        bot.send_message(user_id, f"📬 Ответ от АН BFS:\n\n{message.text}")
        bot.send_message(message.chat.id, "✅ Ответ отправлен")
    else:
        # Пересылка сообщения админам
        username = message.from_user.username or "без username"
        text = message.text or "[пусто]"
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("💬 Ответить", callback_data=f"reply_{message.chat.id}"))
        
        for admin_id in ADMIN_CHAT_IDS:
            try:
                bot.send_message(
                    admin_id,
                    f"📨 Новое сообщение от @{username} (ID: {message.chat.id}):\n\n{text}",
                    reply_markup=markup
                )
            except Exception as e:
                logger.error(f"Error sending to admin {admin_id}: {e}")
        
        bot.send_message(message.chat.id, "✅ Сообщение передано администраторам")

@bot.callback_query_handler(func=lambda call: call.data.startswith("reply_"))
def handle_reply(call):
    user_id = int(call.data.split("_")[1])
    admin_reply_state[call.message.chat.id] = user_id
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, f"✍️ Введите ответ для пользователя {user_id}")

if __name__ == "__main__":
    logger.info("Starting bot...")
    bot.infinity_polling()

import os
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise ValueError("❌ Ошибка: переменная окружения TELEGRAM_BOT_TOKEN не задана!")

ADMIN_CHAT_IDS = [1559058125]  # Добавь своих админов

bot = telebot.TeleBot(BOT_TOKEN)

# Храним состояния: кто из админов в режиме ответа и на чей чат_id
admin_reply_state = {}

@bot.message_handler(commands=["start"])
def start_handler(message):
    bot.send_message(message.chat.id, "👋 Здравстуйте! Напишите своё сообщение для АН BFS.")

@bot.message_handler(func=lambda message: True)
def user_message_handler(message):
    if message.chat.id in ADMIN_CHAT_IDS and message.chat.id in admin_reply_state:
        # Если админ находится в режиме ответа
        user_id = admin_reply_state.pop(message.chat.id)
        bot.send_message(user_id, f"📬 Ответ от АН BFS:\n\n{message.text}")
        bot.send_message(message.chat.id, "✅ Ответ отправлен.")
    else:
        # Пользователь отправляет сообщение — пересылаем его админам с кнопкой
        username = message.from_user.username or "без username"
        user_id = message.chat.id
        text = message.text or "[пусто]"

        reply_markup = InlineKeyboardMarkup()
        reply_markup.add(InlineKeyboardButton("💬 Ответить", callback_data=f"reply_{user_id}"))

        for admin_id in ADMIN_CHAT_IDS:
            bot.send_message(
                admin_id,
                f"📨 Новое сообщение от @{username} (chat_id: {user_id}):\n\n{text}",
                reply_markup=reply_markup
            )

        bot.send_message(user_id, "✅ Спасибо! Ваше сообщение передано.")

@bot.callback_query_handler(func=lambda call: call.data.startswith("reply_"))
def handle_reply_button(call):
    user_id = int(call.data.split("_")[1])
    admin_reply_state[call.message.chat.id] = user_id
    bot.answer_callback_query(call.id)
    bot.send_message(call.message.chat.id, f"✍️ Напишите ответ для chat_id: {user_id}")

print("Бот с кнопкой 'Ответить' запущен...")
bot.polling(non_stop=True)

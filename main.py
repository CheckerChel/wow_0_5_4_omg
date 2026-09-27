import telebot
import os

token = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(token)
CHATS = [-1003724538567, 7163427034]

@bot.message_handler(content_types=['text', 'photo', 'audio', 'document', 'sticker', 'video', 'video_note', 'voice', 'location', 'contact'], func=lambda message: message.via_bot is not None)
def delete_inline_calls(message):
    if message.chat.id not in CHATS:
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            pass

print("есть")
bot.infinity_polling()
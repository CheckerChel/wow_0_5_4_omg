import os
import telebot

token = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(token)
CHATS = [-1003724538567, 7163427034]

@bot.message_handler(func=lambda m: m.chat.id in CHATS)
def check_emojis(message):
    entities = message.entities or getattr(message, 'caption_entities', None)
    
    if entities:
        for ent in entities:
            if ent.type == "custom_emoji":
                try:
                    bot.delete_message(message.chat.id, message.message_id)
                    print(f"Удалено сообщение с кастомным эмодзи в чате {message.chat.id}")
                except Exception as e:
                    print(f"Не удалось удалить сообщение: {e}. Проверьте права бота в чате!")
                return

print("Бот успешно запущен и слушает чаты...")
bot.infinity_polling()
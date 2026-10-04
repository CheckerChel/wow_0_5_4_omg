import os
import telebot

token = os.getenv("BOT_TOKEN")
bot = telebot.TeleBot(token)
CHATS = [-1003724538567, 7163427034]


@bot.message_handler(func=lambda m: m.chat.id in CHATS)
def check_emojis(message):
    entities = message.entities or message.caption_entities
    if entities:
        for ent in entities:
            if ent.type == "custom_emoji":
                try:
                    bot.delete_message(message.chat.id, message.message_id)
                except Exception:
                    pass
                return


print("есть")
bot.infinity_polling()
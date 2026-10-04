import os
import telebot

token = os.getenv("BOT_TOKEN")
if not token:
    raise ValueError("BOT_TOKEN environment variable is not set")

bot = telebot.TeleBot(token)
CHATS = [-1003724538567, 7163427034]
STOP_WORDS = ["@yamexa"]


def should_delete(message) -> bool:
    if message.reply_to_message and message.reply_to_message.from_user:
        if message.reply_to_message.from_user.id in CHATS:
            return True

    if message.location is not None:
        return True

    text_to_check = message.text or message.caption
    if text_to_check:
        for word in STOP_WORDS:
            if word in text_to_check:
                return True

    entities = message.entities or getattr(message, 'caption_entities', None)
    if entities:
        for ent in entities:
            if ent.type == "custom_emoji":
                return True

    return False


@bot.message_handler(func=lambda m: m.chat.id in CHATS, content_types=['text', 'location', 'photo', 'video', 'document', 'audio', 'voice'])
def handle_new_messages(message):
    if should_delete(message):
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            pass


@bot.edited_message_handler(func=lambda m: m.chat.id in CHATS, content_types=['location', 'text'])
def handle_edited_messages(message):
    if should_delete(message):
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            pass


if __name__ == "__main__":
    bot.infinity_polling()
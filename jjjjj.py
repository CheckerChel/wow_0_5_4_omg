import os
import sqlite3
import telebot
import re

TOKEN = os.getenv("BOT_TOKEN")
ALL_ID = [7163427034, -1003724538567]

bot = telebot.TeleBot(TOKEN)

os.makedirs("data", exist_ok=True)
db_path = "data/j_db.db"

conn = sqlite3.connect(db_path, check_same_thread=False)
cursor = conn.cursor()
cursor.execute("""
CREATE TABLE IF NOT EXISTS settings (
    id INTEGER PRIMARY KEY DEFAULT 1,
    inline INTEGER DEFAULT 1,
    ads INTEGER DEFAULT 1
)
""")
cursor.execute("INSERT OR IGNORE INTO settings (id, inline, ads) VALUES (1, 1, 1)")
conn.commit()

def get_settings():
    cursor.execute("SELECT inline, ads FROM settings WHERE id = 1")
    res = cursor.fetchone()
    return {"inline": bool(res[0]), "ads": bool(res[1])}

def update_setting(key, val):
    cursor.execute(f"UPDATE settings SET {key} = ? WHERE id = 1", (1 if val else 0,))
    conn.commit()

@bot.message_handler(func=lambda msg: msg.from_user and msg.from_user.id in ALL_ID, content_types=['text'])
def admin_commands(message):
    text = message.text.strip().lower()
    if text == "+инлайн":
        update_setting("inline", True)
        bot.reply_to(message, "Удаление инлайн-ботов включено.")
    elif text == "-инлайн":
        update_setting("inline", False)
        bot.reply_to(message, "Удаление инлайн-ботов выключено.")
    elif text == "+реклама":
        update_setting("ads", True)
        bot.reply_to(message, "Удаление ссылок/каналов включено.")
    elif text == "-реклама":
        update_setting("ads", False)
        bot.reply_to(message, "Удаление ссылок/каналов выключено.")

@bot.message_handler(func=lambda msg: not (msg.from_user and msg.from_user.id in ALL_ID), content_types=['text', 'audio', 'document', 'photo', 'sticker', 'video', 'video_note', 'voice', 'location', 'contact'])
def filter_messages(message):
    cfg = get_settings()

    if cfg["inline"] and message.via_bot:
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            pass
        return

    if message.sender_chat and message.sender_chat.type in ['channel', 'group', 'supergroup']:
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            pass
        return

    if message.forward_from_chat and message.forward_from_chat.type == 'channel':
        try:
            bot.delete_message(message.chat.id, message.message_id)
        except Exception:
            pass
        return

    if cfg["ads"]:
        text = message.text or message.caption
        if text and message.entities:
            for entity in message.entities:
                if entity.type == "mention":
                    mention_text = text[entity.offset:entity.offset + entity.length]
                    try:
                        chat = bot.get_chat(mention_text)
                        if chat.type in ['channel', 'group', 'supergroup']:
                            bot.delete_message(message.chat.id, message.message_id)
                            return
                    except Exception:
                        pass

                elif entity.type in ["url", "text_link"]:
                    url = entity.url if entity.type == "text_link" else text[entity.offset:entity.offset + entity.length]
                    url = url.lower()
                    
                    if "t.me/" in url or "telegram.me/" in url:
                        match = re.search(r"t\.me/(?:joinchat/|\+)?([^/?#]+)", url)
                        if match:
                            target = match.group(1)
                            if target.startswith("+") or "joinchat" in url:
                                try:
                                    bot.delete_message(message.chat.id, message.message_id)
                                    return
                                except Exception:
                                    pass
                            else:
                                try:
                                    chat = bot.get_chat(f"@{target}")
                                    if chat.type in ['channel', 'group', 'supergroup']:
                                        bot.delete_message(message.chat.id, message.message_id)
                                        return
                                except Exception:
                                    pass

if __name__ == "__main__":
    print("есть")
    bot.infinity_polling()
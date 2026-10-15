import os
import sqlite3
import telebot
import re

TOKEN = os.getenv("BOT_TOKEN")
ALL_ID = [7163427034, -1003724538567]
NOT_BOTS=["sounds", "gif", "pic", "vid", "clips", "music", "sticker", "gamebot", "gamee", "playmixbot"]
WIN_TARGET=[7163427034]

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

class Filter(telebot.SimpleCustomFilter):
    key = "imc"
    def check(self, obj):
        c_id = obj.chat.id if hasattr(obj, "chat") else getattr(obj.message, "chat").id
        return c_id in ALL_ID or obj.from_user.id in ALL_ID

bot.add_custom_filter(Filter())



@bot.message_handler(imc=True, func=lambda msg: msg.from_user and msg.from_user.id in ALL_ID, content_types=['text'])
def admin_commands(message):
    text = message.text.strip().lower()
    if text == "+инлайн":
        update_setting("inline", True)
        bot.reply_to(message, "🪓Инлайн-ботам пизда")
    elif text == "-инлайн":
        update_setting("inline", False)
        bot.reply_to(message, "🫧Инлайн-ботов пощадили")
    elif text == "+реклама":
        update_setting("ads", True)
        bot.reply_to(message, "🪓Минус реклама")
    elif text == "-реклама":
        update_setting("ads", False)
        bot.reply_to(message, "🫧Плюс реклама")

@bot.message_handler(imc=True, func=lambda msg: not (msg.from_user and msg.from_user.id in ALL_ID), content_types=['text', 'audio', 'document', 'photo', 'sticker', 'video', 'video_note', 'voice', 'location', 'contact'])
def filter_messages(message):
    cfg = get_settings()

    if cfg["inline"] and message.via_bot:
        via_bot_username = message.via_bot.username.lower() if message.via_bot.username else ""
        if via_bot_username not in NOT_BOTS:
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

@bot.message_handler(content_types=['dice'])
def check_darts_win(message):
    if message.dice.emoji == "🎯" and message.dice.value == 6:
        user = message.from_user
        first_name = user.first_name
        
        for sym in r"_*[]()~`>#+-=|{}.!":
            first_name = first_name.replace(sym, f"\\{sym}")
        
        user_link = f"[{first_name}](tg://user?id={user.id})"
        chat_id_str = str(message.chat.id).replace("-100", "")
        
        if message.chat.type in ['group', 'supergroup']:
            msg_link = f"https://t.me{chat_id_str}/{message.message_id}"
        else:
            msg_link = f"https://t.me{user.username}/{message.message_id}" if user.username else "https://t.me"

        msg_link_escaped = msg_link.replace(".", "\\.")
        text_to_send = f"🍎{user_link}\n[🚬🗿]({msg_link_escaped})"
        
        for target_id in WIN_TARGET:
            try:
                bot.send_message(chat_id=target_id, text=text_to_send, parse_mode="MarkdownV2")
            except Exception:
                pass

if __name__ == "__main__":
    print("есть")
    bot.infinity_polling()
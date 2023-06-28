import sqlite3
from config import settings
bot = settings["BOT"]


async def clear(current_chat_id):
    try:
        with sqlite3.connect("messages.db") as con:
            cur = con.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS messages (chat_id INTEGER, message_id INTEGER)""")

            for chat_id, message_id in cur.execute("""SELECT * FROM messages""").fetchall():
                if chat_id == current_chat_id:
                    await bot.delete_message(chat_id, message_id=message_id)

            cur.execute(f"""DELETE FROM messages WHERE chat_id == (?);""", (current_chat_id, ))
    except Exception as ex:
        print(ex)


def add_id(chat_id, message_id):
    with sqlite3.connect("messages.db") as con:
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS messages (chat_id INTEGER, message_id INTEGER)""")
        cur.execute("""INSERT INTO messages VALUES (?, ?)""", (chat_id, message_id,))

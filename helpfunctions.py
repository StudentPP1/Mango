import sqlite3


async def clear(message):
    try:
        with sqlite3.connect("messages.db") as con:
            cur = con.cursor()
            cur.execute("""CREATE TABLE IF NOT EXISTS messages (message_id INTEGER)""")

            for message_id in cur.execute("""SELECT * FROM messages""").fetchall():
                print(message_id[0])
                await message.chat.delete_message(message_id=message_id[0])

            cur.execute("""DELETE FROM messages""")
    except Exception as ex:
        print(ex)


def add_id(message_id):
    with sqlite3.connect("messages.db") as con:
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS messages (message_id INTEGER)""")
        cur.execute("""INSERT INTO messages VALUES (?)""", (message_id,))

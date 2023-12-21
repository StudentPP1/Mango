from aiogram.utils import executor
from keyboard import kb_client, kb_restart
import aiogram
from aiogram import types
import sqlite3
from config import settings
from helpfunctions import clear, add_id
from functions import load_music, create_playlist, choose_playlist, delete_playlist, delete_music

bot = settings["BOT"]
dp = settings["DISPATCHER"]


def check(chat_id):
    with sqlite3.connect("users.db") as con:
        cur = con.cursor()
        info = cur.execute("""SELECT * FROM users""").fetchone()
        if not (info is None):
            for group_id in cur.execute("""SELECT group_id FROM users""").fetchall():
                if group_id[0] == chat_id:
                    user_id = cur.execute("""SELECT user_id FROM users WHERE group_id == (?);""", (chat_id,)
                                          ).fetchone()[0]
                    return user_id
            return None
        else:
            return None


async def on_startup(_):
    print("Bot connected")


load_music.register_handlers(dp)
create_playlist.register_handlers(dp)
choose_playlist.register_handlers(dp)
delete_playlist.register_handlers(dp)
delete_music.register_handlers(dp)


@dp.message_handler(commands=["start", "help"])
async def start(message: types.Message):
    def user_not_in_db(cursor, user):
        info = cursor.execute("""SELECT * FROM users""").fetchone()
        if info is None:
            return True
        else:
            for user_id, group_id in cursor.execute("""SELECT * FROM users""").fetchall():
                if user == user_id and group_id != 0:
                    return False
            return True

    with sqlite3.connect("users.db") as con:
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS users 
        (user_id INTEGER PRIMARY KEY, 
        group_id INTEGER)""")

        if user_not_in_db(cur, message.from_user.id):
            cur.execute("""INSERT OR REPLACE INTO users VALUES (?, ?)""", (message.from_user.id, 0))

            msg = await bot.send_message(message.from_user.id, "To get started you need to create a group with the bot "
                                                               "and make it an administrator")
            add_id(message.from_user.id, msg.message_id)
            print("Chat with user:", message.from_user.id)
            await message.delete()
        else:
            await message.delete()
            await clear(message.from_user.id)
            await bot.send_message(message.from_user.id, "Hello it's music bot in which you can:\n"
                                                         "1) Make or delete playlists\n"
                                                         "2) Add or del music from playlists\n"
                                                         "Enjoy listening!)", reply_markup=kb_client)


@dp.my_chat_member_handler()  # detected creating group with bot
async def my_chat_member(message: types.Message) -> None:
    try:
        is_admin = False
        while not is_admin:
            print("waiting...")
            members = await bot.get_chat_administrators(message.chat.id)
            for member in members:
                if member.user.id == bot.id:
                    is_admin = True

        members = await bot.get_chat_administrators(message.chat.id)
        with sqlite3.connect("users.db") as con:
            cur = con.cursor()

            for user_id in cur.execute("""SELECT user_id FROM users WHERE group_id == 0""").fetchall():
                for member in members:
                    if member.user.id == user_id[0]:
                        cur.execute("""UPDATE OR REPLACE users SET group_id = (?) WHERE user_id == (?);""",
                                    (message.chat.id, user_id[0]))
                        print("Group with user:", message.chat.id)
                        await bot.send_message(user_id[0], "Hello it's music bot in which you can:\n"
                                                           "1) Make or delete playlists\n"
                                                           "2) Add or del music from playlists\n"
                                                           "Enjoy listening!)", reply_markup=kb_client)
                        break

    except aiogram.utils.exceptions.BotKicked:
        try:
            with sqlite3.connect("users.db") as con:
                cur = con.cursor()
                info = cur.execute("""SELECT * FROM users""").fetchone()
                if not (info is None):
                    print(f"Bot kicked from {message.chat.id}")
                    for group_id in cur.execute("""SELECT group_id FROM users""").fetchall():
                        if message.chat.id == group_id[0]:
                            user_id = cur.execute("""SELECT user_id FROM users WHERE group_id == (?);""",
                                                  (group_id[0],)).fetchone()

                            await clear(user_id[0])
                            await bot.send_message(user_id[0], "To get started you need to create a group with the bot "
                                                               "and make it an administrator",
                                                   reply_markup=kb_restart)

                            cur.execute(f"""DELETE FROM users WHERE group_id == (?);""", (group_id[0],))
        except Exception as ex:
            print(ex)


@dp.message_handler(content_types=types.ContentType.AUDIO)
async def forward_audio(message: types.Message):
    chat_id = message.chat.id

    user_id = check(chat_id)
    if not (user_id is None):

        with sqlite3.connect("users.db") as con:
            cur = con.cursor()
            group_id = cur.execute(f"""SELECT group_id FROM users WHERE user_id == {user_id}""").fetchone()[0]

        msg_id = message.message_id
        text = str(message.audio.as_json()).split(':')[2].split(",")[0].replace(".mp3", '').replace('"', '')

        print(chat_id, msg_id, text)
        with sqlite3.connect("music.db") as con:
            cur = con.cursor()
            cur.execute(f"""CREATE TABLE IF NOT EXISTS music (
                   group_id INTEGER,
                   user_id INTEGER,
                   track_name TEXT,
                   message_id INTEGER
                   )""")

            cur.execute(f"""INSERT OR IGNORE INTO music VALUES (?, ?, ?, ?)""",
                        (group_id, user_id, text, msg_id,))
    else:
        await message.delete()


@dp.message_handler()
async def get_msg_id(message: types.Message):
    print(message.message_id, type(message.message_id))
    add_id(message.from_user.id, message.message_id)

executor.start_polling(dp, on_startup=on_startup)

from aiogram import types
from config import settings
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import os
import sqlite3
from keyboard import kb_client
from helpfunctions import add_id, clear
from functions.loader import download

bot = settings["BOT"]


def load_track(group_id, user_id, track_name, message_id):
    with sqlite3.connect("music.db") as con:
        cur = con.cursor()
        cur.execute(f"""CREATE TABLE IF NOT EXISTS music (
        group_id INTEGER,
        user_id INTEGER,
        track_name TEXT,
        message_id INTEGER
        )""")
        cur.execute(f"""INSERT OR IGNORE INTO music VALUES (?, ?, ?, ?)""",
                    (group_id, user_id, track_name, message_id,))


class FSMALoader(StatesGroup):
    url = State()


async def start_loader(message: types.Message):
    user_id = message.from_user.id
    await clear(user_id)

    msg = await message.reply("Enter the url: ")
    add_id(user_id, msg.message_id)
    add_id(user_id, message.message_id)

    print(message.message_id, type(message.message_id))
    await FSMALoader.url.set()


async def input_url(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    with sqlite3.connect("users.db") as con:
        cur = con.cursor()
        group_id = cur.execute("""SELECT group_id FROM users WHERE user_id == (?);""", (user_id,)).fetchone()[0]

    add_id(user_id, message.message_id)

    print(message.message_id, type(message.message_id))
    try:
        music_files = download(message.text)

        for music_file in music_files:
            media = types.MediaGroup()
            media.attach_audio(types.InputFile(music_file), music_file.split('\\')[-1])

            msg1 = await bot.send_media_group(chat_id=group_id, media=media)

            load_track(group_id, user_id, music_file.split('\\')[-1], msg1[0]["message_id"])

            msg2 = await message.reply("Done", reply_markup=kb_client)

            add_id(user_id, msg2.message_id)
            os.remove(music_file)

    except Exception as ex:
        print(ex)
        msg = await message.reply("Sorry, I have some problem with this url, please try other url")
        add_id(user_id, msg.message_id)

    await state.finish()


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_loader, lambda message: "Load music" in message.text, state=None)
    dp.register_message_handler(input_url, state=FSMALoader.url)

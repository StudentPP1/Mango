from aiogram import types
from config import settings
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
import os
import sqlite3
from helpfunctions import add_id, clear
from functions.loader import download

bot = settings["BOT"]
group_id = settings["GROUP_ID"]


def load_track(name, message_id):
    with sqlite3.connect("tracks.db") as con:
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS tracks (name TEXT, message_id INTEGER)""")
        cur.execute("""INSERT INTO tracks VALUES (?, ?)""", (name, message_id,))


class FSMALoader(StatesGroup):
    url = State()


async def start_loader(message: types.Message):
    await clear(message)
    msg = await message.reply("Enter the url: ")
    add_id(msg.message_id)
    add_id(message.message_id)
    print(message.message_id, type(message.message_id))
    await FSMALoader.url.set()


async def input_url(message: types.Message, state: FSMContext):
    add_id(message.message_id)

    print(message.message_id, type(message.message_id))
    try:
        music_files = download(message.text)

        for music_file in music_files:
            media = types.MediaGroup()
            media.attach_audio(types.InputFile(music_file), music_file.split('\\')[-1])

            msg1 = await bot.send_media_group(chat_id=group_id, media=media)

            load_track(music_file.split('\\')[-1], msg1[0]["message_id"])

            msg2 = await message.reply("Done")

            add_id(msg2.message_id)
            os.remove(music_file)

    except Exception as ex:
        print(ex)

        msg = await message.reply("Sorry, I have some problem with this url, please try other url")
        add_id(msg.message_id)

    await state.finish()


def register_handlers(dp: Dispatcher):
    dp.register_message_handler(start_loader, lambda message: "Load music" in message.text, state=None)
    dp.register_message_handler(input_url, state=FSMALoader.url)

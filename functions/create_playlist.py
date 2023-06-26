from aiogram import types
from config import settings
import re
from googletrans import Translator
# pip install googletrans==3.1.0a0
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
import sqlite3
from helpfunctions import add_id, clear

bot = settings["BOT"]
chat_id = settings["CHAT_ID"]
group_id = settings["GROUP_ID"]


def create_playlist(name, message_id):
    with sqlite3.connect("tracks.db") as con:
        cur = con.cursor()
        cur.execute(f"""CREATE TABLE IF NOT EXISTS {name} (message_id INTEGER)""")
        cur.execute(f"""INSERT OR IGNORE INTO {name} VALUES (?)""", (message_id,))


class FSMACreatePlaylist(StatesGroup):
    name = State()


async def start_creating(message: types.Message):
    await clear(message)
    msg = await message.reply("Enter the name of new playlist: ")

    add_id(msg.message_id)
    add_id(message.message_id)

    await FSMACreatePlaylist.name.set()


async def name_and_choose(message: types.Message, state: FSMContext):
    if len(message.text) > 10:
        msg = await message.answer("Try again")
        add_id(msg.message_id)
        await state.finish()
    else:
        msg = await message.answer("Choose tracks: ")
        add_id(message.message_id)
        add_id(msg.message_id)
        try:
            with sqlite3.connect("tracks.db") as con:
                cur = con.cursor()

                for message_id in cur.execute("""SELECT * FROM tracks""").fetchall():
                    print(message_id)
                    text = str(message_id[0]).replace(".mp3", "")
                    translator = Translator(service_urls=['translate.googleapis.com'])
                    text = translator.translate(text[:35], dest="en").text
                    text = re.sub('[^a-zA-Z0123456789+-~ ]', '', text).replace('_', '')
                    # if len(text) > 40:
                    #     translator = Translator(service_urls=['translate.googleapis.com'])
                    #     text = translator.translate(text[:40], dest="en").text
                    #     text = re.sub('[^a-zA-Z0123456789+-~ ]', '', text)
                    #     text = text.replace('_', '')

                    callback_data = f"save_{text}_{message.text}_{message_id[1]}"

                    print(callback_data)
                    msg = await message.answer(f"{text}", reply_markup=InlineKeyboardMarkup().add(
                         InlineKeyboardButton(text="+", callback_data=callback_data)))
                    add_id(msg.message_id)

        except Exception as ex:
            print(ex)
            msg = await message.answer("Please add some tracks and come back: ")
            add_id(msg.message_id)

        await state.finish()


async def save_track(callback: types.CallbackQuery):
    try:
        _, track_name, name, track_id = callback.data.split('_')
        create_playlist(name, int(track_id))

        await callback.answer(f"Track: {track_name} saved to {name}")
    except Exception as ex:
        print(ex)
        msg = await callback.answer("Wrong name of playlist: ")


def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(save_track, Text(startswith="save_"))
    dp.register_message_handler(start_creating, lambda message: "Create playlist" in message.text, state=None)
    dp.register_message_handler(name_and_choose, state=FSMACreatePlaylist.name)


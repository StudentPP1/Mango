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


def create_playlist(user_id, playlist_name, track_name, message_id):
    with sqlite3.connect("tracks.db") as con:
        cur = con.cursor()
        cur.execute(f"""CREATE TABLE IF NOT EXISTS {playlist_name}_{user_id} (name TEXT, message_id INTEGER)""")
        cur.execute(f"""INSERT OR IGNORE INTO {playlist_name}_{user_id} VALUES (?, ?)""", (track_name, message_id,))


class FSMACreatePlaylist(StatesGroup):
    name = State()


async def start_creating(message: types.Message):
    await clear(message.from_user.id)
    msg = await message.reply("Enter the name of new playlist: ")

    add_id(message.from_user.id, msg.message_id)
    add_id(message.from_user.id, message.message_id)

    await FSMACreatePlaylist.name.set()


async def name_and_choose(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if len(message.text) > 10:
        msg = await message.answer("Try again")
        add_id(user_id, msg.message_id)
        await state.finish()
    else:
        msg = await message.answer("Choose tracks: ")
        add_id(user_id, msg.message_id)
        add_id(user_id, message.message_id)

        with sqlite3.connect("tracks.db") as con:
            cur = con.cursor()

            for track_message in cur.execute(f"""SELECT * FROM tracks_{user_id}""").fetchall():
                print(track_message)
                text = str(track_message[0]).replace(".mp3", "")
                # translator = Translator(service_urls=['translate.googleapis.com'])
                # text = translator.translate(text[:35], dest="en").text
                text = re.sub('[^А-яа-яа-яА-яa-zA-Z() ]', '', text).replace('_', '')[:20]
                print(text)
                callback_data = f"save_{text}_{message.text}_{track_message[1]}_{user_id}"

                print(callback_data)
                msg = await message.answer(text, reply_markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton(text="+", callback_data=callback_data)))
                add_id(user_id, msg.message_id)
        # msg = await message.answer("Please add some tracks and come back: ")
        # add_id(user_id, msg.message_id)

        await state.finish()


async def save_track(callback: types.CallbackQuery):
    try:
        _, track_name, playlist_name, track_id, user_id = callback.data.split('_')
        create_playlist(int(user_id), playlist_name, track_name, int(track_id))

        await callback.answer(f"Track: {track_name} saved to {playlist_name}")
    except Exception as ex:
        print(ex)
        await callback.answer("Wrong name of playlist: ")


def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(save_track, Text(startswith="save_"))
    dp.register_message_handler(start_creating, lambda message: "Create playlist" in message.text, state=None)
    dp.register_message_handler(name_and_choose, state=FSMACreatePlaylist.name)


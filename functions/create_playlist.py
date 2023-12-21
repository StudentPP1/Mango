from aiogram import types
from config import settings
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters.state import State, StatesGroup
import sqlite3
from helpfunctions import add_id, clear
from keyboard import kb_client

bot = settings["BOT"]


def create_playlist(user_id, playlist_name, message_id):
    with sqlite3.connect("playlist.db") as con:
        cur = con.cursor()
        cur.execute(f"""CREATE TABLE IF NOT EXISTS {playlist_name}_{user_id} (message_id INTEGER)""")
        cur.execute(f"""INSERT OR IGNORE INTO {playlist_name}_{user_id} VALUES (?)""", (message_id,))


class CreatePlaylistState(StatesGroup):
    name = State()


async def start_creating(message: types.Message):
    await clear(message.from_user.id)
    msg = await message.reply("Enter the name of new playlist: ")

    add_id(message.from_user.id, msg.message_id)
    add_id(message.from_user.id, message.message_id)

    await CreatePlaylistState.name.set()


async def name_and_choose(message: types.Message, state: FSMContext):
    user_id = message.from_user.id

    if len(message.text) > 20:
        msg = await message.answer("Name is too long")
        add_id(user_id, msg.message_id)
        await state.finish()
    else:
        msg = await message.answer("Choose tracks: ")
        add_id(user_id, msg.message_id)
        add_id(user_id, message.message_id)

        is_send = False
        with sqlite3.connect("music.db") as con:
            cur = con.cursor()

            for track_message in cur.execute(f"""SELECT * FROM music WHERE user_id == {user_id}""").fetchall():
                print(track_message)
                group_id, user_id, track_name, message_id = track_message
                print(track_name)

                callback_data = f"save_{message.text}_{message_id}_{user_id}"

                print(callback_data)
                msg = await message.answer(track_name, reply_markup=InlineKeyboardMarkup().add(
                        InlineKeyboardButton(text="+", callback_data=callback_data)))
                add_id(user_id, msg.message_id)
                is_send = True

        if not is_send:
            msg = await message.answer("Please add some tracks and come back: ", reply_markup=kb_client)
            add_id(user_id, msg.message_id)

        await state.finish()


async def save_track(callback: types.CallbackQuery):
    try:
        _, playlist_name, track_id, user_id = callback.data.split('_')
        create_playlist(int(user_id), playlist_name, int(track_id))

        await callback.answer(f"Track saved to {playlist_name}")
    except Exception as ex:
        print(ex)
        await callback.answer("Wrong name of playlist: ")


def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(save_track, Text(startswith="save_"))
    dp.register_message_handler(start_creating, lambda message: "Create playlist" in message.text, state=None)
    dp.register_message_handler(name_and_choose, state=CreatePlaylistState.name)

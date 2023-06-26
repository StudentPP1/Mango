from aiogram import types
from config import settings
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from helpfunctions import add_id, clear
import sqlite3

bot = settings["BOT"]
chat_id = settings["CHAT_ID"]
group_id = settings["GROUP_ID"]


async def start_deleting(message: types.Message):
    await clear(message)

    msg = await message.answer("Choose playlist: ")
    add_id(msg.message_id)
    add_id(message.message_id)

    with sqlite3.connect("tracks.db") as con:
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        count = 1
        for playlist in cur.fetchall():
            if playlist[0] != "tracks":
                callback_data = f"delete_{playlist[0]}"
                print(callback_data)
                msg = await message.answer(f"{count}: ", reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton(text=playlist[0], callback_data=callback_data)))
                add_id(msg.message_id)
                count += 1


async def delete_playlist(callback: types.CallbackQuery):
    _, playlist_name = callback.data.split('_')

    with sqlite3.connect("tracks.db") as con:
        cur = con.cursor()
        cur.execute(f"DROP TABLE {playlist_name};")

    await callback.answer(f"Playlist: {playlist_name} deleted")


def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(delete_playlist, Text(startswith="delete_"))
    dp.register_message_handler(start_deleting, lambda message: "Delete playlist" in message.text)

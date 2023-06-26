from aiogram import types
from config import settings
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text
from helpfunctions import add_id, clear
import sqlite3

bot = settings["BOT"]
chat_id = settings["CHAT_ID"]
group_id = settings["GROUP_ID"]


async def choose_playlist(message: types.Message):
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
                callback_data = f"choose_{playlist[0]}"
                print(callback_data)
                msg = await message.answer(f"{count}: ", reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton(text=playlist[0], callback_data=callback_data)))
                add_id(msg.message_id)
                count += 1


async def send_playlist(callback: types.CallbackQuery):
    await clear(callback)
    _, playlist_name = callback.data.split('_')

    msg = await bot.send_message(chat_id, f"Playlist: {playlist_name}")
    add_id(msg.message_id)

    with sqlite3.connect("tracks.db") as con:
        cur = con.cursor()
        for message_id in cur.execute(f"SELECT * FROM {playlist_name}").fetchall():
            msg = await bot.forward_message(chat_id, group_id, message_id[0])
            add_id(msg.message_id)
    await callback.answer()


def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(send_playlist, Text(startswith="choose_"))
    dp.register_message_handler(choose_playlist, lambda message: "Choose playlist" in message.text, state=None)


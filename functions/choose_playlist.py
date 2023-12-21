from aiogram import types
from config import settings
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher import Dispatcher
from aiogram.dispatcher.filters import Text
from helpfunctions import add_id, clear
import sqlite3

from keyboard import kb_client

bot = settings["BOT"]


async def choose_playlist(message: types.Message):
    user_id = message.from_user.id

    await clear(user_id)
    msg = await message.answer("Choose playlist: ")
    add_id(user_id, msg.message_id)
    add_id(user_id, message.message_id)

    is_send = False
    with sqlite3.connect("playlist.db") as con:
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        count = 1
        for playlist in cur.fetchall():
            if playlist[0] != f"tracks_{user_id}" and str(user_id) in playlist[0]:
                callback_data = f"choose_{playlist[0]}"
                print(callback_data)
                msg = await message.answer(f"{count}: ", reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton(text=playlist[0].split('_')[0], callback_data=callback_data)))
                add_id(user_id, msg.message_id)
                count += 1
                is_send = True

    if not is_send:
        msg = await message.answer("Please create a playlist: ", reply_markup=kb_client)
        add_id(user_id, msg.message_id)


async def send_playlist(callback: types.CallbackQuery):
    _, playlist_name, user_id = callback.data.split('_')
    await clear(user_id)

    msg = await bot.send_message(int(user_id), f"Playlist: {playlist_name}", reply_markup=kb_client)
    add_id(int(user_id), msg.message_id)

    with sqlite3.connect("users.db") as con:
        cur = con.cursor()
        group_id = cur.execute("""SELECT group_id FROM users WHERE user_id == (?);""", (user_id,)).fetchone()[0]

    with sqlite3.connect("playlist.db") as con:
        cur = con.cursor()
        for message_id in cur.execute(f"SELECT * FROM {playlist_name}_{user_id}").fetchall():
            msg = await bot.forward_message(user_id, group_id, message_id[0])
            add_id(int(user_id), msg.message_id)

    await callback.answer()


def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(send_playlist, Text(startswith="choose_"))
    dp.register_message_handler(choose_playlist, lambda message: "Choose playlist" in message.text, state=None)

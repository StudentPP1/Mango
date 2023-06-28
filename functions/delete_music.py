from aiogram import types
from config import settings
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import Dispatcher
import re
from googletrans import Translator
# pip install googletrans==3.1.0a0
from helpfunctions import add_id, clear
import sqlite3

bot = settings["BOT"]


async def deleting_music(message: types.Message):
    user_id = message.from_user.id
    with sqlite3.connect("users.db") as con:
        cur = con.cursor()
        group_id = cur.execute("""SELECT group_id FROM users WHERE user_id == (?);""", (user_id,)).fetchone()[0]

    await clear(user_id)

    msg = await message.answer("Choose tracks: ")
    add_id(user_id, message.message_id)
    add_id(user_id, msg.message_id)

    with sqlite3.connect("tracks.db") as con:
        cur = con.cursor()
        count = 1
        for message_id in cur.execute(f"""SELECT * FROM tracks_{user_id}""").fetchall():
            print(message_id)
            text = str(message_id[0]).replace(".mp3", "")
            text = re.sub('[^А-яа-яа-яА-яa-zA-Z() ]', '', text).replace('_', '')[:20]

            callback_data = f"del_{text}_{message_id[1]}_{group_id}"
            print(callback_data)
            msg = await message.answer(f"{count}: ", reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton(text=text, callback_data=callback_data)))
            add_id(user_id, msg.message_id)
            count += 1


async def del_track(callback: types.CallbackQuery):
    _, track_name, track_id, group_id = callback.data.split('_')
    print(int(group_id), int(track_id))
    await bot.delete_message(int(group_id), int(track_id))

    with sqlite3.connect("tracks.db") as con:
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        for table in cur.fetchall():
            cur.execute(f"DELETE FROM {table[0]} WHERE message_id = {int(track_id)}")

    await callback.answer(f"Track: {track_name} deleted")


def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(del_track, Text(startswith="del_"))
    dp.register_message_handler(deleting_music, lambda message: "Delete music" in message.text, state=None)

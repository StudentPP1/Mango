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
chat_id = settings["CHAT_ID"]
group_id = settings["GROUP_ID"]


async def deleting_music(message: types.Message):
    await clear(message)

    msg = await message.answer("Choose tracks: ")
    add_id(message.message_id)
    add_id(msg.message_id)

    with sqlite3.connect("tracks.db") as con:
        cur = con.cursor()
        count = 1
        for message_id in cur.execute("""SELECT * FROM tracks""").fetchall():
            print(message_id)
            text = str(message_id[0]).replace(".mp3", "")
            if len(text) > 40:
                text1 = re.sub('[^a-zA-Z0123456789+_-~ ]', '', text[:42])
                if text1 == '':
                    translator = Translator(service_urls=['translate.googleapis.com'])
                    text = translator.translate(text[:40], dest="en").text
                else:
                    text = text1

            callback_data = f"del_{text}_{message_id[1]}"
            print(callback_data)
            msg = await message.answer(f"{count}: ", reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton(text=text, callback_data=callback_data)))
            add_id(msg.message_id)
            count += 1


async def del_track(callback: types.CallbackQuery):
    _, track_name, track_id = callback.data.split('_')
    await bot.delete_message(group_id, int(track_id))

    with sqlite3.connect("tracks.db") as con:
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        for table in cur.fetchall():
            cur.execute(f"DELETE FROM {table[0]} WHERE message_id = {int(track_id)}")

    await callback.answer(f"Track: {track_name} deleted")


def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(del_track, Text(startswith="del_"))
    dp.register_message_handler(deleting_music, lambda message: "Delete music" in message.text, state=None)

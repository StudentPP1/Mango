from aiogram import types
from config import settings
from keyboard import kb_delete_music, kb_client
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.dispatcher.filters import Text
from aiogram.dispatcher import Dispatcher
from helpfunctions import add_id, clear
import sqlite3

bot = settings["BOT"]


async def deleting_music(message: types.Message):
    await clear(message.from_user.id)
    user_id = message.from_user.id

    msg = await message.answer("Delete music from:", reply_markup=kb_delete_music)
    add_id(user_id, msg.message_id)
    add_id(user_id, message.message_id)


async def delete_from_music_list(message: types.Message):
    user_id = message.from_user.id

    msg = await message.answer("Choose track:", reply_markup=kb_client)
    add_id(user_id, msg.message_id)
    add_id(user_id, message.message_id)

    is_send = False
    with sqlite3.connect("music.db") as con:
        cur = con.cursor()
        for track_message in cur.execute(f"""SELECT * FROM music WHERE user_id == {user_id}""").fetchall():
            group_id, user_id, track_name, track_id = track_message
            callback_data = f"del_{track_id}_{group_id}"
            msg = await message.answer(track_name, reply_markup=InlineKeyboardMarkup().add(
                InlineKeyboardButton(text="-", callback_data=callback_data)))
            add_id(user_id, msg.message_id)
            is_send = True

    if not is_send:
        msg = await message.answer("Please add some tracks and come back: ", reply_markup=kb_client)
        add_id(user_id, msg.message_id)


async def set_name_playlist(message: types.Message):
    user_id = message.from_user.id
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
                callback_data = f"p_{playlist[0]}"
                print(callback_data)
                msg = await message.answer(f"{count}: ", reply_markup=InlineKeyboardMarkup().add(
                    InlineKeyboardButton(text=playlist[0].split('_')[0], callback_data=callback_data)))
                add_id(user_id, msg.message_id)
                count += 1
                is_send = True

        if not is_send:
            msg = await message.answer("Please create a playlist: ", reply_markup=kb_client)
            add_id(user_id, msg.message_id)


async def delete_from_playlist(callback: types.CallbackQuery):
    _, playlist_name, user_id = callback.data.split('_')

    msg = await bot.send_message(chat_id=user_id, text="Choose track:", reply_markup=kb_client)
    add_id(user_id, msg.message_id)

    music = []
    with sqlite3.connect("playlist.db") as con:
        cur = con.cursor()
        for message_id in cur.execute(f"SELECT * FROM {playlist_name}_{user_id}").fetchall():
            music.append(message_id[0])

    with sqlite3.connect("music.db") as con:
        cur = con.cursor()
        for track_message in cur.execute(f"""SELECT * FROM music WHERE user_id == {user_id}""").fetchall():
            group_id, user_id, track_name, track_id = track_message
            if track_id in music:
                callback_data = f"del_{track_id}_{group_id}"
                msg = await bot.send_message(chat_id=user_id, text=track_name,
                                             reply_markup=InlineKeyboardMarkup().add(
                                                              InlineKeyboardButton(text="-",
                                                                                   callback_data=callback_data)))
                add_id(user_id, msg.message_id)


async def del_track(callback: types.CallbackQuery):
    _, track_id, group_id = callback.data.split('_')
    print(int(group_id), int(track_id))
    await bot.delete_message(int(group_id), int(track_id))

    with sqlite3.connect("playlist.db") as con:
        cur = con.cursor()
        cur.execute("SELECT name FROM sqlite_master WHERE type='table';")
        for table in cur.fetchall():
            cur.execute(f"DELETE FROM {table[0]} WHERE message_id = {int(track_id)}")

    with sqlite3.connect("music.db") as con:
        cur = con.cursor()
        cur.execute(f"DELETE FROM music WHERE message_id = {int(track_id)} AND group_id = {int(group_id)};")

    await callback.answer("Track deleted")


def register_handlers(dp: Dispatcher):
    dp.register_callback_query_handler(del_track, Text(startswith="del_"))
    dp.register_message_handler(deleting_music, lambda message: "Delete music" in message.text)
    dp.register_message_handler(delete_from_music_list, lambda message: "all music list" in message.text)
    dp.register_message_handler(set_name_playlist, lambda message: "choose playlist" in message.text)
    dp.register_callback_query_handler(delete_from_playlist, Text(startswith="p_"))

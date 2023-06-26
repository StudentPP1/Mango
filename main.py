from aiogram.utils import executor
from keyboard import kb_client
from aiogram import types
import sqlite3
from config import settings
from helpfunctions import clear, add_id
from functions import load_music, create_playlist, choose_playlist, delete_playlist, delete_music


bot = settings["BOT"]
dp = settings["DISPATCHER"]
chat_id = settings["CHAT_ID"]
group_id = settings["GROUP_ID"]


async def on_startup(_):
    print("Bot connected")


load_music.register_handlers(dp)
create_playlist.register_handlers(dp)
choose_playlist.register_handlers(dp)
delete_playlist.register_handlers(dp)
delete_music.register_handlers(dp)


@dp.message_handler(commands=["start", "help"])
async def start(message: types.Message):
    await clear(message)
    msg = await bot.send_message(message.from_user.id, "Hello it's music bot in which you can:\n"
                                                 "1) Make or delete playlists\n"
                                                 "2) Add or del music from playlists\n"
                                                 "Enjoy listening!)", reply_markup=kb_client)
    await message.delete()


todo: "зробити бота універсальним (записувати id в базу даних) + переробити доступ до баз даних"


@dp.my_chat_member_handler()  # detected creating group with bot
async def my_chat_member(message: types.Message) -> None:
    print(message.chat.id)


@dp.message_handler(content_types=types.ContentType.AUDIO)
async def forward_audio(message: types.Message):
    msg_id = message.message_id
    text = str(message.audio.as_json()).split(':')[2].split(",")[0].replace(".mp3", '').replace('"', '')

    with sqlite3.connect("tracks.db") as con:
        cur = con.cursor()
        cur.execute("""CREATE TABLE IF NOT EXISTS tracks (name TEXT, message_id INTEGER)""")
        cur.execute("""INSERT INTO tracks VALUES (?, ?)""", (text, msg_id,))


@dp.message_handler()
async def get_msg_id(message: types.Message):
    print(message.message_id, type(message.message_id))

    add_id(message.message_id)

executor.start_polling(dp, on_startup=on_startup)

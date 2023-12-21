from aiogram.types import ReplyKeyboardMarkup, KeyboardButton

b1, b2, b3 = KeyboardButton("Choose playlist"), KeyboardButton("Create playlist"), KeyboardButton("Delete playlist")
b4, b5 = KeyboardButton("Load music"), KeyboardButton("Delete music")

kb_client = ReplyKeyboardMarkup(resize_keyboard=True)

kb_client.row(b4, b5)
kb_client.row(b1)
kb_client.row(b2)
kb_client.row(b3)

kb_restart = ReplyKeyboardMarkup(resize_keyboard=True).row(KeyboardButton("/start"))

kb_delete_music = ReplyKeyboardMarkup(resize_keyboard=True)\
    .row(KeyboardButton("all music list"))\
    .row(KeyboardButton("choose playlist"))\
    .row(KeyboardButton("/start"))

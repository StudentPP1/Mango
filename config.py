import os
from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

bot = Bot(token=os.getenv("TOKEN"))
storage = MemoryStorage()

settings = {"BOT": bot,
            "DISPATCHER": Dispatcher(bot, storage=storage)}

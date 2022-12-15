from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils import executor


from config import TOKEN
import requests
import asyncio
import os


BASE_MEDIA_PATH = '\\media'
channel_id = -898695733  #ls_id = 886669764

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)


@dp.message_handler()
async def echo_message(msg: types.Message):
    print(msg.text)
    await bot.send_message(msg.chat.id, msg.text)


if __name__ == '__main__':
    executor.start_polling(dp)


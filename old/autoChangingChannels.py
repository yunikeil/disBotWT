import discord
from discord.ext import commands

import os
import shutil
import json

bot = commands.Bot(command_prefix='>', intents=discord.Intents.all())
created_channels = []

"""
created_channels = [1042163498400092160: 286914074422280194, 123:321]
"""


# Сделать подгрузку остальных переменных а также проверку
# на оставленные чаты при резком завершении программы.


@bot.event
async def on_ready():
    global created_channels
    data_path = os.getcwd() + '\\data'
    for guild_id in os.listdir(path=data_path):
        guild_path = data_path + f'\\{guild_id}'
        with open(guild_path + '\\canals.txt') as file:
            created_channels = file.readlines()

    print(f'We have logged in as {bot.user}')
    print(created_channels)



@bot.event
async def on_voice_state_update(member, before, after):
    data_path = os.getcwd() + '\\data'
    if str(member.guild.id) not in os.listdir(path=data_path):
        # Проверка на регистрацию каналов...
        return
    else:
        main_canals_json = json.load(open(f"{data_path}\\{str(member.guild.id)}\\main_canals.json"))
    print(main_canals_json)

    global created_channels

    # after использовать для вновь присоединившихся пользователей
    # такжу тут будут создаваться каналы в created_channels и canals.txt
    if after.channel:
        print(f"after: {after.channel.id} admin: {member.id}")

    # before использовать для тех кто покидает канал.
    # такжу тут будут удаляться каналы из created_channels и canals.txt
    if before.channel:
        print(f"before: {before.channel.id} admin: {member.id}")


bot.run('MTAzNzQ3NzYzMzQxMzM0OTQwNg.Gkf8md.qskApsB1XKWa7d3A4zOKdzszi3r8yhXqlGUwnk')

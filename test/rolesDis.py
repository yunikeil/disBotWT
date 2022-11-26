import discord
from discord.ext import commands

import configuration
import asyncio
from datetime import datetime


bot = commands.Bot(command_prefix='>', intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.event
async def on_member_join(member):
    # Можно через sleep, можно через запись в файл и каждые 20 минут чекать новых пользователей
    #await asyncio.sleep(20*60)
    # Тут проверка на то есть ли роль спустя 20 минут
    # Если роли нет, тогда ставим автоматом обе роли


    pass


@bot.command()
async def info(ctx):
    await ctx.send("info command!")


bot.run(configuration.token)

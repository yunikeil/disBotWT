import discord
import asyncio
from discord.ext import commands
from discord import app_commands
import os

intents = discord.Intents.all()
intents.message_content = True

bot = commands.Bot(command_prefix='.', intents=intents)


@bot.event
async def on_ready():
    print('Online.')


async def load():
    for filename in os.listdir('cogs'):
        if filename.endswith('.py'):
            await bot.load_extension(f'cogs.{filename[:-3]}')


async def main():
    await load()
    await bot.start('MTAzNzQ3NzYzMzQxMzM0OTQwNg.GYfQls.5wj55LV8mcPWTcHyz--Ip8O48ngO9D_iExZAWE')


asyncio.run(main())

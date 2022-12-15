import discord
from discord.ext import commands

import configuration


bot = commands.Bot(command_prefix='>', intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.command()
async def info(ctx):
    await ctx.send(f"{bot.get_user(1037477633413349406).avatar}")



bot.run(configuration.token)

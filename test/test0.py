import discord
from discord.ext import commands

import configuration


bot = commands.Bot(command_prefix='>', intents=discord.Intents.all())
channels = []


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


# Notepad++
@bot.command()
async def c(ctx):
    global channels

    channels = ctx.author.guild.channels

    ##

    for channel in channels:
        print(type(channel), end=" ")
        print(f"\t{channel.name}\t{channel.id}")


"""@bot.command()
async def p(ctx):
    global channels

    for channel in channels:
        print(type(channel), end=" ")
        print(channel.name)"""


@bot.command()
async def info(ctx):
    await ctx.send("info command!")


bot.run(configuration.token)

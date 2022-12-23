import discord
from discord.ext import commands


import os

bot = commands.Bot(command_prefix="!", intents=discord.Intents.all())
bot.remove_command("help")


@bot.command()
async def load(ctx, extensions):
    await bot.load_extension(f"cogs.{extensions}")
    await ctx.send('loaded')


@bot.command()
async def unload(ctx, extension):
    await bot.unload_extension(f"cogs.{extension}")
    await ctx.send('unloaded')


@bot.command()
async def reload(ctx, extension):
    await bot.unload_extension(f"cogs.{extension}")
    await bot.load_extension(f"cogs.{extension}")


@bot.event
async def on_ready():
    for filename in os.listdir("./cogs"):
        if filename.endswith(".py"):
            await bot.load_extension("cogs." + filename[:-3])


bot.run('MTAzNzQ3NzYzMzQxMzM0OTQwNg.GYfQls.5wj55LV8mcPWTcHyz--Ip8O48ngO9D_iExZAWE')

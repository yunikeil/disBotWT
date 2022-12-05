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
    await asyncio.sleep(20 * 60)
    member = member
    guild = member.guild
    ru_role_id = configuration.ru_role_id
    en_role_id = configuration.en_role_id
    if member.get_role(ru_role_id) is None and member.get_role(en_role_id) is None:
        await member.add_roles(guild.get_role(ru_role_id))
        await member.add_roles(guild.get_role(en_role_id))


    pass


@bot.command()
async def info(ctx):
    await ctx.setn("info_command!")



bot.run(configuration.token)

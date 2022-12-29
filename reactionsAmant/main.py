import discord
from discord.ext import commands


aman_id = 632552306398724106
## test4
## kill <pid>
## disown

bot = commands.Bot(command_prefix='>', intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.event
async def on_raw_reaction_add(payload: discord.RawReactionActionEvent):
    # удаляет реакции с моего сообщения от амантура
    channel = bot.get_channel(payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)
    if payload.user_id == aman_id and msg.author.id == 286914074422280194:
        for reaction in msg.reactions:
            await reaction.remove(bot.get_user(aman_id))


@bot.event
async def on_raw_reaction_clear(payload: discord.RawReactionActionEvent):
    # удаление всех реакций с какого либо сообщения
    channel = bot.get_channel(payload.channel_id)
    msg = await channel.fetch_message(payload.message_id)
    if msg.author.id == aman_id:
        await msg.add_reaction('🤡')


@bot.event
async def on_message(message):
    if message.author.id == aman_id:
        await message.add_reaction('🤡')

#bot.run('MTA1NjE3Njk4MDA3NDE3MjQ3Nw.Gcvkgh.N5KKsjKLPilTcK6bC-PGwJ-VeUydSMo78rD8tY')
#bot.run('MTAzNzQ3NzYzMzQxMzM0OTQwNg.GYfQls.5wj55LV8mcPWTcHyz--Ip8O48ngO9D_iExZAWE')
import discord
from discord.ext import commands


intents = discord.Intents.default()
intents.message_content = True


client = discord.Client(intents=intents)


@client.event
async def on_ready():
    print(f'We have logged in as {client.user}')


@client.event
async def on_message(message):
    if message.author == client.user:
        return

    print(message)
    if message.content.startswith('$'):
        await message.channel.send('123')


@client.event
async def on_voice_state_update(member, before, after):
    #text_channel = client.get_channel(1040695064889933968)
    #await text_channel.send(member+"\n")
    if after.channel and after.channel.id == 899793728594653198:
        print(member, member.id)




client.run('MTAzNzQ3NzYzMzQxMzM0OTQwNg.Gkf8md.qskApsB1XKWa7d3A4zOKdzszi3r8yhXqlGUwnk')


from typing import Optional

from typing import Literal, Union, NamedTuple
from enum import Enum

import discord
from discord import app_commands

import requests
import configuration
import urllib.parse

MY_GUILD = discord.Object(id=configuration.guild_id)  # replace with your guild id


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        # This copies the global commands over to your guild.
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


intents = discord.Intents.default()
client = MyClient(intents=intents)


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')


"""
Допустии у меня есть 5 комманд anime_add anime_del anime_for anime_find
как их оюъединить в одну /anime "выпадающий список" "тут для каждый своя команда" 
"""


# Чтобы сделать аргумент необязательным, вы можете либо присвоить ему поддерживаемый аргумент по умолчанию
# или вы можете пометить его как необязательный в стандартной библиотеке набора текста. В этом примере выполняется и то, и другое.
@client.tree.command()
@app_commands.describe(service='выберите тип взаимодействия', url='если требуется загрузка изображения')
async def anime(interaction: discord.Interaction, service: Literal['поиск аниме по картинке', 'рандомная цитата'],
                url: Optional[str] = None):
    global last_iteraction
    """Выбор приложения для взаимодействия"""
    if service == 'поиск аниме по картинке':
        if url and "https://" in url:
            # last_iteraction = проверка на использование раз в минуту
            json_get = requests.get("https://api.trace.moe/search?url={}"
                                    .format(urllib.parse.quote_plus(str(url)))
                                    ).json()['result']
            for element in json_get:
                pass
            anilist = json_get[0]['anilist']
            filename = json_get[0]['filename']
            episode = json_get[0]['episode']
            from_ = json_get[0]['from']
            to = json_get[0]['to']
            similarity = json_get[0]['similarity']
            video = json_get[0]['video']
            image = json_get[0]['image']
            embed = discord.Embed(title=filename)
            embed.add_field(name='List: ', value=f'1/{int(len(json_get))}', inline=False)
            embed.add_field(name='Anilist number: ', value=anilist, inline=False)
            embed.add_field(name='Filename: ', value=filename, inline=False)
            embed.add_field(name='Episode: ', value=episode, inline=False)
            embed.add_field(name='Moment from: ', value=from_, inline=False)
            embed.add_field(name='Moment to: ', value=to, inline=False)
            embed.add_field(name='Similarity: ', value=similarity, inline=False)
            embed.set_image(url=image)
            url_view = discord.ui.View()
            url_view.add_item(discord.ui.Button(label='Ссылка на отрывок с моментом',
                                                style=discord.ButtonStyle.url, url=video))
            await interaction.response.send_message(embed=embed, view=url_view)
        else:
            await interaction.response.send_message("Неверное url", ephemeral=True)
    if service == 'рандомная цитата':
        # last_iteraction = проверка на использование раз в минуту
        json_get = requests.get('https://animechan.vercel.app/api/random').json()
        embed = discord.Embed(title=json_get['character'])
        embed.description = json_get['quote']
        embed.set_footer(text=f"Anime: {json_get['anime']}")
        await interaction.response.send_message(embed=embed)


client.run(configuration.token)

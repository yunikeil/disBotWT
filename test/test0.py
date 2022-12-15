# Этот пример основан на концепциях app_commands/basic.py пример
# Предлагается сначала взглянуть на это, чтобы понять определенные концепции.

from typing import Literal, Union, NamedTuple
from enum import Enum

import discord
from discord import app_commands

import configuration


MY_GUILD = discord.Object(id=configuration.guild_id)


class MyClient(discord.Client):
    def __init__(self):
        super().__init__(intents=discord.Intents.default())
        self.tree = app_commands.CommandTree(self)

    async def setup_hook(self):
        self.tree.copy_global_to(guild=MY_GUILD)
        await self.tree.sync(guild=MY_GUILD)


client = MyClient()


@client.event
async def on_ready():
    print(f'Logged in as {client.user} (ID: {client.user.id})')
    print('------')


# Трансформатор - это класс, который определяет, как параметр в вашем коде
# должен вести себя как при использовании в Discord, так и при получении его из Discord.
# Есть несколько встроенных трансформаторов, в этом примере они будут показаны вместе с
# создайте свой собственный для максимальной гибкости.

# Первый встроенный трансформатор - это app_commands.Диапазон
# Он работает с опциями `str`, `int` и `float` и сообщает вам
# допустимые максимальное и минимальное значения (или длина в случае `str`)


@client.tree.command()
@app_commands.describe(first='The first number to add', second='The second number to add')
async def add(
    interaction: discord.Interaction,
    # Это делает так, что первый параметр может быть только в диапазоне от 0 до 100.
    first: app_commands.Range[int, 0, 100],
    # Это делает так, что второй параметр должен быть больше 0, без максимального ограничения.
    second: app_commands.Range[int, 0, None],
):
    """Adds two numbers together"""
    await interaction.response.send_message(f'{first} + {second} = {first + second}', ephemeral=True)


# Другие трансформаторы включают обычные подсказки типа, поддерживаемые Discord
# Примеры из них включают int, str, float, bool, User, Member, Role и любой тип канала.
# Поскольку их много, для краткости будет включен только пример канала.

# Эта команда показывает, как показывать пользователю только текстовые и голосовые каналы, используя подсказку типа объединения
# # в сочетании с типами VoiceChannel и TextChannel.
@client.tree.command(name='channel-info')
@app_commands.describe(channel='The channel to get info of')
async def channel_info(interaction: discord.Interaction, channel: Union[discord.VoiceChannel, discord.TextChannel]):
    """Shows basic channel info for a text or voice channel."""

    embed = discord.Embed(title='Channel Info')
    embed.add_field(name='Name', value=channel.name, inline=True)
    embed.add_field(name='ID', value=channel.id, inline=True)
    embed.add_field(
        name='Type',
        value='Voice' if isinstance(channel, discord.VoiceChannel) else 'Text',
        inline=True,
    )

    embed.set_footer(text='Created').timestamp = channel.created_at
    await interaction.response.send_message(embed=embed)


# Для поддержки выбора в библиотеке есть несколько способов сделать это.
# Первый - это использование набора текста.Буквальный для основных вариантов.

# В Discord это будет отображаться как два варианта: покупка и продажа.
# В коде вы получите либо 'Buy', либо 'Sell' в виде строки.
@client.tree.command()
@app_commands.describe(action='The action to do in the shop', item='The target item')
async def shop(interaction: discord.Interaction, action: Literal['Buy', 'Sell'], item: str):
    """Interact with the shop"""
    await interaction.response.send_message(f'Action: {action}\nItem: {item}')


# Второй способ сделать выбор - это использовать перечисление из стандартной библиотеки
# # В Discord это будет отображаться в виде четырех вариантов: яблоко, банан, вишня и драконий фрукт
# В коде вы получите соответствующее значение enum.

class Fruits(Enum):
    apple = 0
    banana = 1
    cherry = 2
    dragonfruit = 3


@client.tree.command()
@app_commands.describe(fruit='The fruit to choose')
async def fruit(interaction: discord.Interaction, fruit: Fruits):
    """Choose a fruit!"""
    await interaction.response.send_message(repr(fruit))


# Вы также можете создать свой собственный трансформатор, унаследовав его от app_commands.Трансформатор

class Point(NamedTuple):
    x: int
    y: int


# Преобразователь по умолчанию принимает строковый параметр, и вы можете преобразовать
# Преобразуйте его в любое значение, которое вы пожелаете.
#
# Трансформаторы также поддерживают различные другие настройки, такие как переопределение
# такие свойства, как `choices`, `max_value`, `min_value`, `type` или `channel_types`.
# Однако это выходит за рамки данного примера, поэтому ознакомьтесь с документацией
# для получения дополнительной информации.
class PointTransformer(app_commands.Transformer):
    async def transform(self, interaction: discord.Interaction, value: str) -> Point:
        (x, _, y) = value.partition(',')
        return Point(x=int(x.strip()), y=int(y.strip()))


@client.tree.command()
async def graph(
    interaction: discord.Interaction,
    # In order to use the transformer, you should use Transform to tell the
    # library to use it.
    point: app_commands.Transform[Point, PointTransformer],
):
    await interaction.response.send_message(str(point))


# Для более простых трансформаторов для ваших собственных типов без слишком большого повторения,
# поддерживается концепция, известная как "встроенные трансформаторы". Это позволяет вам использовать
# # метод класса для создания преобразователя на основе строк. Это только полезно
# если вы заботитесь только о преобразовании строки в класс и ни о чем другом.
class Point3D(NamedTuple):
    x: int
    y: int
    z: int

    # # Это то же самое, что и приведенный выше трансформатор, за исключением встроенного
    @classmethod
    async def transform(cls, interaction: discord.Interaction, value: str):
        x, y, z = value.split(',')
        return cls(x=int(x.strip()), y=int(y.strip()), z=int(z.strip()))


@client.tree.command()
async def graph3d(interaction: discord.Interaction, point: Point3D):
    await interaction.response.send_message(str(point))


client.run(configuration.token)

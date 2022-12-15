from typing import Optional

import discord
from discord import app_commands

import configuration

MY_GUILD = discord.Object(id=configuration.guild_id)  # replace with your guild id


class MyClient(discord.Client):
    def __init__(self, *, intents: discord.Intents):
        super().__init__(intents=intents)
        # # Дерево команд - это особый тип, который содержит все команды приложения
        # состояние, необходимое для того, чтобы это заработало. Это отдельный класс, потому что он
        # позволяет включить все дополнительные состояния.
        # Всякий раз, когда вы хотите работать с командами приложения, используется ваше дерево
        # для хранения и работы с ними.
        # Примечание: При использовании команд.Бот вместо дискорда.Клиент, бот будет
        # вместо этого поддерживайте свое собственное дерево.
        self.tree = app_commands.CommandTree(self)

    # В этом базовом примере мы просто синхронизируем команды приложения с одной гильдией.
    # Вместо того, чтобы указывать гильдию для каждой команды, вместо этого мы копируем наши глобальные команды.
    # Поступая таким образом, нам не нужно ждать до часа, пока они не будут показаны конечному пользователю.
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


@client.tree.command()
async def hello(interaction: discord.Interaction):
    """Says hello!!!"""
    await interaction.response.send_message(f'Hi, {interaction.user.mention}')


@client.tree.command()
@app_commands.describe(
    first_value='The first value you want to add something to',
    second_value='The value you want to add to the first value',
)
async def add(interaction: discord.Interaction, first_value: int, second_value: int):
    """Adds two numbers together."""
    await interaction.response.send_message(f'{first_value} + {second_value} = {first_value + second_value}')


# Декоратор переименования позволяет нам изменить отображение параметра в Discord.
# В этом примере, несмотря на то, что мы используем `text_to_send` в коде, клиент будет использовать `text` вместо этого.
# Обратите внимание, что другие декораторы по-прежнему будут ссылаться на него как на `text_to_send` в коде.
@client.tree.command()
@app_commands.rename(text_to_send='text')
@app_commands.describe(text_to_send='Text to send in the current channel')
async def send(interaction: discord.Interaction, text_to_send: str):
    """Sends the text into the current channel."""
    await interaction.response.send_message(text_to_send)


# Чтобы сделать аргумент необязательным, вы можете либо присвоить ему поддерживаемый аргумент по умолчанию
# или вы можете пометить его как необязательный в стандартной библиотеке набора текста. В этом примере выполняется и то, и другое.
@client.tree.command()
@app_commands.describe(member='The member you want to get the joined date from; defaults to the user who uses the command')
async def joined(interaction: discord.Interaction, member: Optional[discord.Member] = None):
    """Says when a member joined."""
    # Если ни один участник явно не указан, то здесь мы используем команду user
    member = member or interaction.user

    # Функция format_dt форматирует дату и время в удобочитаемое представление в официальном клиенте
    await interaction.response.send_message(f'{member} joined {discord.utils.format_dt(member.joined_at)}')


# Команда контекстного меню - это команда приложения, которая может быть запущена для участника или сообщения с помощью
# доступ к меню внутри клиента, обычно с помощью щелчка правой кнопкой мыши.
# Он всегда принимает взаимодействие в качестве своего первого параметра и участника или сообщение в качестве второго параметра.

# Эта команда контекстного меню работает только с участниками
@client.tree.context_menu(name='Show Join Date')
async def show_join_date(interaction: discord.Interaction, member: discord.Member):
    # Функция format_dt форматирует дату и время в удобочитаемое представление в официальном клиенте
    await interaction.response.send_message(f'{member} joined at {discord.utils.format_dt(member.joined_at)}')


# Эта команда контекстного меню работает только с сообщениями
@client.tree.context_menu(name='Report to Moderators')
async def report_message(interaction: discord.Interaction, message: discord.Message):
    # Мы отправляем это ответное сообщение с ephemeral=True, поэтому только исполнитель команды может его увидеть
    await interaction.response.send_message(
        f'Thanks for reporting this message by {message.author.mention} to our moderators.', ephemeral=True
    )

    # Обработайте отчет, отправив его в канал журнала
    log_channel = interaction.guild.get_channel(1052747375355113513)  # replace with your channel id

    embed = discord.Embed(title='Reported Message')
    if message.content:
        embed.description = message.content

    embed.set_author(name=message.author.display_name, icon_url=message.author.display_avatar.url)
    embed.timestamp = message.created_at

    url_view = discord.ui.View()
    url_view.add_item(discord.ui.Button(label='Go to Message', style=discord.ButtonStyle.url, url=message.jump_url))

    await log_channel.send(embed=embed, view=url_view)


client.run(configuration.token)

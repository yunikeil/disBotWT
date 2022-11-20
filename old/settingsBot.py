import discord
from discord.ext import commands

bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
main_text_channel = ""
main_voice_channel = ""


class HumanToKickSelect(discord.ui.Select):
    def __init__(self, user_voice_channel_id):
        # time_out устананавливается в классе View(discord.ui.View) в функции вызова.
        ## Добавить проверку на админа голосового чата.
        self.user_voice_channel_id = user_voice_channel_id
        self.members_on_create = bot.get_channel(self.user_voice_channel_id).members
        options = []
        for member in self.members_on_create:
            options.append(
                discord.SelectOption(label=f"{member.name}", value=f"{member}")
            )
        super().__init__(placeholder="Люди в канале: ", max_values=1, min_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        if bot.get_channel(self.user_voice_channel_id) is None:
            await interaction.response.send_message("Канал пустой, или не существует", ephemeral=True)
            return
        members_on_callback = bot.get_channel(self.user_voice_channel_id).members
        human_in_canal = False
        click_button_human_in_canal = False
        for member in members_on_callback:
            if str(interaction.user) == str(member):
                click_button_human_in_canal = True
        if click_button_human_in_canal:
            for member in members_on_callback:
                if str(self.values[0]) == str(member):
                    human_in_canal = True
                    await member.move_to(None)
                    await interaction.response.send_message("Человек удалён с канала.", ephemeral=True)
            if not human_in_canal: await interaction.response.send_message(
                "Данного человека нет в канала.", ephemeral=True)
        else:
            await interaction.response.send_message(
                "Вы находитесь вне канала, которым пытаетесь управлять.", ephemeral=True)


class LimitButtonModal(discord.ui.Modal, title='Лимит людей'):
    def __init__(self, user_voice_channel_id, timeout=180):
        super().__init__(timeout=timeout)
        self.user_voice_channel_id = user_voice_channel_id

    limit = discord.ui.TextInput(
        label='Лимит',
        placeholder='Введите лимит людей...',
        min_length=1,
        max_length=2,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        voice_channel = bot.get_channel(self.user_voice_channel_id)
        await voice_channel.edit(user_limit=self.limit.value)
        await interaction.response.send_message(
            content=f"Лимит людей изменён до: {self.limit}",
            ephemeral=True
        )

    async def on_error(self, interaction: discord.Interaction, error):
        # Добавить сюда логгер
        pass


class RenameButtonModal(discord.ui.Modal, title='Переименовать'):
    def __init__(self, user_voice_channel_id, timeout=180):
        super().__init__(timeout=timeout)
        self.user_voice_channel_id = user_voice_channel_id

    name = discord.ui.TextInput(
        label='Новое имя',
        placeholder='Введите новое имя...',
        min_length=5,
        max_length=50,
        required=False
    )

    async def on_submit(self, interaction: discord.Interaction):
        voice_channel = bot.get_channel(self.user_voice_channel_id)
        await voice_channel.edit(name=self.name.value)
        await interaction.response.send_message(
            content=f"Имя канала изменено на: {self.name.value}",
            ephemeral=True
        )

    async def on_error(self, interaction: discord.Interaction, error):
        # Добавить сюда логгер
        pass


class VoiceButtons(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.timeout = None

    @staticmethod
    async def checkCanal(interaction):
        # Сюда добавить проверку является ли КАНАЛ ПОД УПРАВЛЕНИЕ БОТА
        # Для тестирование установлено значение вручную созданного канала.
        created_our_servers = [1041389445217275904, 1041389483888746577]
        if interaction.user.voice and interaction.user.voice.channel.id in created_our_servers:
            return True, interaction.user.voice.channel.id
        else:
            await interaction.response.send_message(
                content=f"Вы находитесь вне действующего канала,"
                        f" или зоны действия бота.",
                ephemeral=True
            )
            return False, None

    @discord.ui.button(label="Лимит людей", style=discord.ButtonStyle.primary, row=1)
    async def limit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        isBool, user_voice_channel_id = await self.checkCanal(interaction)
        if isBool:
            await interaction.response.send_modal(
                LimitButtonModal(user_voice_channel_id=user_voice_channel_id)
            )

    @discord.ui.button(label="Переименовать", style=discord.ButtonStyle.primary, row=1)
    async def rename_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        isBool, user_voice_channel_id = await self.checkCanal(interaction)
        if isBool:
            await interaction.response.send_modal(
                RenameButtonModal(user_voice_channel_id=user_voice_channel_id)
            )

    @discord.ui.button(label="Закрыть канал", style=discord.ButtonStyle.primary, row=1)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        isBool, user_voice_channel_id = await self.checkCanal(interaction)
        if isBool:
            voice_channel = bot.get_channel(user_voice_channel_id)
            members = voice_channel.members
            await voice_channel.edit(user_limit=len(members))
            await interaction.response.send_message(
                content=f"Канал закрыт.",
                ephemeral=True
            )

    @discord.ui.button(label="Открыть канал", style=discord.ButtonStyle.primary, row=1)
    async def open_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        isBool, user_voice_channel_id = await self.checkCanal(interaction)
        if isBool:
            voice_channel = bot.get_channel(user_voice_channel_id)
            await voice_channel.edit(user_limit=0)
            await interaction.response.send_message(
                content=f"Канал открыт.",
                ephemeral=True
            )

    @discord.ui.button(label="Выгнать участника", style=discord.ButtonStyle.secondary, row=2)
    async def kick_out_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        isBool, user_voice_channel_id = await self.checkCanal(interaction)
        if isBool:
            class View(discord.ui.View):
                def __init__(self, *, timeout=180):
                    super().__init__(timeout=timeout)
                    self.add_item(HumanToKickSelect(user_voice_channel_id=user_voice_channel_id))

                async def on_timeout(self):
                    self.clear_items()

            await interaction.response.send_message(
                content="Выберите участника, которого необходима кикнуть: ",
                ephemeral=True,
                view=View()
            )

    @discord.ui.button(label="test", style=discord.ButtonStyle.danger, row=2)
    async def test_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            content="test button!",
            ephemeral=True
        )


## для тех кто любит спамит можно пробовать эту функцию https://qna.habr.com/q/925267
## проверку для того подходит или нет канал можно завернуть в предикат https://ru.stackoverflow.com/questions/1369564

## это функция только для отладки, в будущем будет полностью переписана.
@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')
    voice_control_text = bot.get_channel(1042058995663392768)
    await voice_control_text.purge()
    embed = discord.Embed(
        title="Бот для голосовых",
        colour=discord.Colour.blurple(),
        description=f"Чат для управления: <#{1042058995663392768}>\n"
                    f"Главный голосовой чат: <#{1042059323746046043}>\n"
    )
    embed.set_image(url="http://lluban.by/images/storage/news/000509_818136_big.jpg")
    embed.set_thumbnail(url='https://memepedia.ru/wp-content/uploads/2018/08/dlydryywsaa1jp8-768x576.jpg')
    embed.set_footer(text='© WTServer 2022')

    await voice_control_text.send(
        view=VoiceButtons(),
        embed=embed,
    )


## Почитать про ограничения дискорда на отправку запросов, сделать ограничения на слишком частые запросы для
# пользователей, 1, 2, 3 - можно сразу сделать, следующие только по прошествию минуты
bot.run('MTAzNzQ3NzYzMzQxMzM0OTQwNg.Gkf8md.qskApsB1XKWa7d3A4zOKdzszi3r8yhXqlGUwnk')

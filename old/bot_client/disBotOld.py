import discord
from discord.ext import commands


bot = commands.Bot(command_prefix='!', intents=discord.Intents.all())
# button.style = discord.ButtonStyle.green

class Buttons(discord.ui.View):  # класс описывает набор кнопок
    def __init__(self, *, timeout=180):  # конструктор класса
        super().__init__(timeout=timeout)

    @discord.ui.button(label="primary", style=discord.ButtonStyle.primary)
    async def primary_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        #await interaction.response.edit_message(content=f"primary!")
        await interaction.response.send_message(content=f"primary!", ephemeral=True)

    @discord.ui.button(label="secondary", style=discord.ButtonStyle.secondary)
    async def secondary_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content=f"secondary!")

    @discord.ui.button(label="success", style=discord.ButtonStyle.success)
    async def success_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content=f"success!")

    @discord.ui.button(label="danger", style=discord.ButtonStyle.danger)
    async def danger_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.edit_message(content=f"danger!")


# Лимит человек
#  https://cdn.discordapp.com/emojis/950433575893889094.webp?size=44&quality=lossless

# Переименовать
#  https://cdn.discordapp.com/emojis/950496898563866684.webp?size=44&quality=lossless


@bot.event
async def on_ready():
    voice_control_text = bot.get_channel(1040695064889933968)
    await voice_control_text.purge()
    await voice_control_text.send(
        "This message has buttons!",  # текст сообщения как обычно
        view=Buttons()  # создаём экземпляр класса Buttons и прикрепляем его
    )
    print(f'We have logged in as {bot.user}')

@bot.command()
async def button(ctx):
    view = Buttons()
    view = view.add_item(item=discord.ui.Button(label="URL Button",
                                                style=discord.ButtonStyle.link,
                                                url="https://github.com/lykn"))
    await ctx.send("This message has buttons!", view=view)

bot.run('MTAzNzQ3NzYzMzQxMzM0OTQwNg.Gkf8md.qskApsB1XKWa7d3A4zOKdzszi3r8yhXqlGUwnk')

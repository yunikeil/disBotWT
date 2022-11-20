import discord
from discord.ext import commands

import os
import shutil
import json


bot = commands.Bot(command_prefix='>', intents=discord.Intents.all())


@bot.event
async def on_ready():
    print(f'We have logged in as {bot.user}')


@bot.command()
async def reg(ctx):
    if not ctx.message.author.guild_permissions.administrator:
        return
    main_canal_data = {}

    async def settings_reset_callback(interaction):
        embed = discord.Embed(
            title="Мастер настройки voice_bot",
            description=f"Настройка прервана!"
        )
        await interaction.response.edit_message(embed=embed, view=None)

    async def settings_step_final_callback(interaction):
        async def final_settings_button_callback(interaction):
            guild_id = ctx.guild.id
            data_path = os.getcwd() + '\\data'
            guild_path = data_path + f'\\{guild_id}'
            if str(guild_id) not in os.listdir(path=data_path):
                os.mkdir(path=guild_path)
                open(guild_path + '\\logs.log', "x").close()
                open(guild_path + '\\logs_errors.log', "x").close()
                main_canals = open(guild_path + '\\main_canals.json', "x")
                main_canals.write(json.dumps(main_canal_data))
                main_canals.close()
                open(guild_path + '\\canals.txt', "x").close()
            else:
                main_canals = open(guild_path + '\\main_canals.json', "w")
                main_canals.write(json.dumps(main_canal_data))
                main_canals.close()

            embed = discord.Embed(
                title="Мастер настройки voice_bot",
                description=f"Настройки сохранены."
            )
            await interaction.response.edit_message(embed=embed, view=None)

        embed = discord.Embed(
            title="Мастер настройки voice_bot",
            description=f"Следующим шагом вы сохраните настройки в файл.\n"
                        f"Или добавите ещё один управляющий канал."
        )

        final_settings_button = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Завершить настройку!"
        )
        final_settings_button.callback = final_settings_button_callback

        new_text_input = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Добоавить ещё один текстовый канал"
        )
        new_text_input.callback = start_settings_callback

        settings_reset_button = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label="Прервать настройку",
            row=2
        )
        settings_reset_button.callback = settings_reset_callback

        await interaction.response.edit_message(
            embed=embed,
            view=discord.ui.View()
            .add_item(item=final_settings_button)
            .add_item(item=settings_reset_button)
            .add_item(item=new_text_input)
        )

    async def settings_step_two_callback(interaction):
        async def choice_voice_channel_button_callback(interaction):
            class VoiceChannelIdInputModal(discord.ui.Modal, title="Введите id главного голосового канала"):
                def __init__(self):
                    super().__init__()

                modal_text_input_item = discord.ui.TextInput(
                    label='Введите id',
                    placeholder='Введите id управляющего голосового канала...',
                    min_length=10,
                    max_length=20,
                    required=False
                )

                async def on_submit(self, interaction: discord.Interaction):
                    if self.modal_text_input_item.value not in voice_canals:
                        voice_canals.append(self.modal_text_input_item.value)
                        global current_text_control_channel_id
                        main_canal_data[current_text_control_channel_id] = voice_canals
                    next_step_on_settings_step_two_callback.disabled = False
                    if len(voice_canals) == 1:
                        embed_description = "Вы выбрали такой голосовой канал:"
                    else:
                        embed_description = "Вы выбрали такие голосовые каналы:"
                    voice_canals_string = ""
                    for voice_canal in voice_canals:
                        voice_canals_string = voice_canals_string + f"<#{voice_canal}>\n"

                    after_id_input_embed = discord.Embed(
                        title="Мастер настройки voice_bot",
                        description=f"{embed_description}\n"
                                    f"{voice_canals_string}"
                    )
                    await interaction.response.edit_message(
                        embed=after_id_input_embed,
                        view=discord.ui.View()
                        .add_item(item=choice_voice_channel_button)
                        .add_item(item=next_step_on_settings_step_two_callback)
                        .add_item(item=settings_reset_button)
                    )

            await interaction.response.send_modal(VoiceChannelIdInputModal())

        voice_canals = []
        start_settings_button_callback_embed = discord.Embed(
            title="Мастер настройки voice_bot",
            description=f"На данном шаге нужно вбить один или несколько"
                        f" id главного голосового канала,"
                        f" на его основе будут создаваться дочерние,"
                        f" нажмите продолжить, когда закончите"
        )

        choice_voice_channel_button = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Нажмите для ввода"
        )
        choice_voice_channel_button.callback = choice_voice_channel_button_callback

        next_step_on_settings_step_two_callback = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Продолжить"
        )
        next_step_on_settings_step_two_callback.disabled = True
        next_step_on_settings_step_two_callback.callback = settings_step_final_callback

        settings_reset_button = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label="Прервать настройку",
            row=2
        )
        settings_reset_button.callback = settings_reset_callback

        await interaction.response.edit_message(
            embed=start_settings_button_callback_embed,
            view=discord.ui.View()
            .add_item(item=choice_voice_channel_button)
            .add_item(item=next_step_on_settings_step_two_callback)
            .add_item(item=settings_reset_button)
        )

    async def start_settings_callback(interaction):
        async def choice_text_channel_button_callback(interaction):
            class TextChannelIdInputModal(discord.ui.Modal, title="Введите id главного голосового канала"):
                def __init__(self):
                    super().__init__()

                modal_text_input_item = discord.ui.TextInput(
                    label='Введите id',
                    placeholder='Введите id управляющего текстового канала...',
                    min_length=10,
                    max_length=20,
                    required=False
                )

                async def on_submit(self, interaction: discord.Interaction):
                    global current_text_control_channel_id
                    current_text_control_channel_id = self.modal_text_input_item.value
                    choice_text_channel_button.disabled = True
                    next_step_on_start_settings_button_callback.disabled = False
                    after_id_input_embed = discord.Embed(
                        title="Мастер настройки voice_bot",
                        description=f"Вы выбрали данный текстовый канал:"
                                    f" <#{self.modal_text_input_item.value}>"
                    )
                    await interaction.response.edit_message(
                        embed=after_id_input_embed,
                        view=discord.ui.View()
                        .add_item(item=choice_text_channel_button)
                        .add_item(item=next_step_on_start_settings_button_callback)
                        .add_item(item=settings_reset_button)
                    )

            await interaction.response.send_modal(TextChannelIdInputModal())

        start_settings_embed = discord.Embed(
            title="Мастер настройки voice_bot",
            description=f"На данном шаге вам нужно будет вбить id управляющего текстового канала"
        )

        choice_text_channel_button = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Нажмите для ввода"
        )
        choice_text_channel_button.callback = choice_text_channel_button_callback

        next_step_on_start_settings_button_callback = discord.ui.Button(
            style=discord.ButtonStyle.primary,
            label="Продолжить"
        )
        next_step_on_start_settings_button_callback.disabled = True
        next_step_on_start_settings_button_callback.callback = settings_step_two_callback

        settings_reset_button = discord.ui.Button(
            style=discord.ButtonStyle.danger,
            label="Прервать настройку",
            row=2
        )
        settings_reset_button.callback = settings_reset_callback

        await interaction.response.edit_message(
            embed=start_settings_embed,
            view=discord.ui.View()
            .add_item(item=choice_text_channel_button)
            .add_item(item=next_step_on_start_settings_button_callback)
            .add_item(item=settings_reset_button)
        )

    embed = discord.Embed(
        title="Мастер настройки voice_bot",
        description=f"Внимание, это служебная команда, выполняйте её"
                    f" только в том случае, если уверены в своих знаниях!\n"
                    f"Пожалуйста, пройдите цикл настройки до конца,"
                    f" не стоит удалять сообщение, или ждать больше 2х минут,"
                    f" в случае ошибки нажмите кнопку 'Прервать настройку'\n"
                    f"Добавить сюда выбор локализации для разных текстовых каналов\n"
                    f"Также это действие сотрёт все ранее настроенные каналы"
    )
    start_settings_button = discord.ui.Button(
        style=discord.ButtonStyle.primary,
        label="Начать настройку!"
    )
    start_settings_button.callback = start_settings_callback
    await ctx.send(embed=embed, view=discord.ui.View().add_item(item=start_settings_button))


@bot.command()
async def info(ctx):
    if not ctx.message.author.guild_permissions.administrator:
        return

    guild_id = ctx.guild.id
    data_path = os.getcwd() + '\\data'
    guild_path = data_path + f'\\{guild_id}'
    if str(guild_id) in os.listdir(path=data_path):
        with open(guild_path + '\\main_canals.json') as json_file:
            main_canals = json.load(json_file)
        description_string = ""
        for data_server in main_canals.items():
            text_channel = data_server[0]
            voice_channels = data_server[1]
            voice_channels_string = ""
            for voice_channel in voice_channels:
                voice_channels_string = voice_channels_string + f"><#{voice_channel}>\n"
            description_string = description_string + f"Текстовый канал: <#{text_channel}>\n" \
                                                      f"{voice_channels_string}\n"
    else:
        embed = discord.Embed(
            title="Просмотр настроек voice_bot",
            description=f"Нет настроек для текущей гильдии."
        )
        await ctx.send(embed=embed)
        return

    embed = discord.Embed(
        title="Просмотр настроек voice_bot",
        description=f"Текущая гильдия: {ctx.guild}\n\n"
                    f"{description_string}"
    )

    await ctx.send(embed=embed)


@bot.command()
async def reset(ctx):
    if not ctx.message.author.guild_permissions.administrator:
        return

    async def reset_settings_button_callback(interaction):
        guild_id = interaction.guild.id
        data_path = os.getcwd() + '\\data'
        guild_path = data_path + f'\\{guild_id}'
        if str(guild_id) in os.listdir(path=data_path):
            shutil.rmtree(guild_path)

            embed = discord.Embed(
                title="Сброс настроек voice_bot",
                description=f"Сброс выполнен.\nИспользуйте >reg  для повторной авторизации каналов."
            )

            await interaction.response.edit_message(embed=embed, view=None)
        else:
            embed = discord.Embed(
                title="Сброс настроек voice_bot",
                description=f"Сброс не выполнен.\nНеудалось найти настройки для данной группы."
            )

            await interaction.response.edit_message(embed=embed, view=None)

    async def reset_cancel_button_callback(interaction):
        embed = discord.Embed(
            title="Сброс настроек voice_bot",
            description=f"Сброс отменён."
        )
        await interaction.response.edit_message(embed=embed, view=None)

    embed = discord.Embed(
        title="Сброс настроек voice_bot",
        description=f"Текущая гильдия: {ctx.guild}\n"
                    f"Внимание! отменить это действие невозможно,"
                    f" это сбросит все настройки для гилдии, включая"
                    f" сохранённые профили пользовательских каналов."
    )

    reset_settings_button = discord.ui.Button(
        style=discord.ButtonStyle.danger,
        label="Сбросить настройки",
        row=2
    )
    reset_settings_button.callback = reset_settings_button_callback

    reset_cancel_button = discord.ui.Button(
        style=discord.ButtonStyle.primary,
        label="Отменить сброс настроек"
    )
    reset_cancel_button.callback = reset_cancel_button_callback

    await ctx.send(
        embed=embed,
        view=discord.ui.View()
        .add_item(item=reset_settings_button)
        .add_item(item=reset_cancel_button)
    )


bot.run('MTAzNzQ3NzYzMzQxMzM0OTQwNg.Gkf8md.qskApsB1XKWa7d3A4zOKdzszi3r8yhXqlGUwnk')

import discord
from discord.ext import commands

import os
import shutil
import json
import copy
import random
import asyncio
import datetime
import logging.handlers

import configuration

bot = commands.Bot(command_prefix='>', intents=discord.Intents.all(), help_command=None)

## Переписать с нуля на sqlite и организовать нормальное взаимодействие с сервером
## Добавить сохранение id сообщений бота в БД
## Доабвить общий логгер на дебаг а также логгер на инфо и ошибки
## И убрать эти дибильный сообщения об ошибка в трай ексепт

# Для тех кто любит спамит можно пробовать эту функцию https://qna.habr.com/q/925267
# Проверку для того подходит или нет канал можно завернуть в предикат https://ru.stackoverflow.com/questions/1369564
# Раз в час: https://ru.stackoverflow.com/questions/1173308/

# global variables
"""
main_canals_json ========>
Включает в себя массив json:
{id текстового канала: [массив id голосовых каналов, управленются левым текстовым]}
{"1042058995663392768": ["1042059323746046043", "1042060242231500891"]}
Редактируется внутри:   
async def reg
async def reset

canals ========>
Включает в себя массив строк, разделённых через двоеточие
id временного канала: id админа канала
1042059323746044572:1042123456746044572
Редактируется внутри:
Функции для создания и удаления каналов           сюда вписать позднее нормальные названия функций
Функции для Запуска бота (удаление пустых и тд)   сюда вписать позднее нормальные названия функций

data_path ========>
Включает в себя путь до папки с настройками
"""
main_canals_json = []
canals_txt = {}
data_path = configuration.data_path
bot_id = configuration.bot_id


# global variables
## Сделать нормальные логи!!!


def update_varns():
    global main_canals_json
    global canals_txt
    global data_path
    global bot_id

    # global main_canals_json
    for guild_id in os.listdir(path=data_path):
        guild_id = int(guild_id)
        guild_path = os.sep.join([data_path, str(guild_id)])
        with open(os.sep.join([guild_path, 'main_canals.json']), 'r') as json_file:
            main_canals_json.append(json.load(json_file))

    # global canals_txt
    for guild_id in os.listdir(path=data_path):
        guild_id = int(guild_id)
        canals_txt[int(guild_id)] = []
        guild_path = os.sep.join([data_path, str(guild_id)])
        # Удаляет повторы
        uniqlines_file = open(os.sep.join([guild_path, 'canals.txt']), 'r', encoding='utf-8')
        uniqlines = uniqlines_file.readlines()
        uniqlines_file.close()
        gotovo_file = open(os.sep.join([guild_path, 'canals.txt']), 'w', encoding='utf-8')
        gotovo_file.writelines(set(uniqlines))
        gotovo_file.close()
        with open(os.sep.join([guild_path, 'canals.txt']), 'r') as txt_file:
            for line in txt_file.readlines():
                canals_txt[int(guild_id)].append(line.replace('\n', ''))


async def update_messages():
    global main_canals_json
    global canals_txt
    global data_path
    global bot_id

    # Удаляет прошлые сообщения для управления и создаёт новые!
    for guild_id in os.listdir(path=data_path):
        guild_path = os.sep.join([data_path, str(guild_id)])
        with open(os.sep.join([guild_path, 'main_canals.json']), 'r') as json_file:
            main_canals = json.load(json_file)
            for data_server in main_canals.items():
                text_channel_id = data_server[0]
                voice_channels = data_server[1]
                text_channel = bot.get_channel(int(text_channel_id))
                voice_channels_string = ""
                for voice_channel in voice_channels:
                    voice_channels_string = voice_channels_string + f"><#{voice_channel}>\n"
                embed = discord.Embed(
                    title="War Thunder Voice",
                    colour=discord.Colour.red(),
                    description=f"Chat for management:\n"
                                f"<#{text_channel_id}>\n"
                                f"Voice channels:\n"
                                f"{voice_channels_string}"
                )
                embed.set_image(url='https://media.discordapp.net/attachments/1039227923980353539/'
                                    '1044481856277585950/maxresdefault_1.jpg?width=960&height=540')
                # embed.set_thumbnail(url='https://memepedia.ru/wp-content/uploads/2018/08/dlydryywsaa1jp8-768x576.jpg')
                embed.set_footer(text='© WTServer 2022')

                ## >control (locale) => en ru
                try:
                    await text_channel.purge(limit=10, check=lambda message: message.author.id == bot_id)
                except:
                    pass
                if text_channel:
                    await text_channel.send(embed=embed, view=VoiceButtons(language=None))
                else: pass


## Каналы не удаляются если их нет в файле
async def update_voice_canals():
    global main_canals_json
    global canals_txt
    global data_path
    global bot_id

    # Удаляет пустые голосовые каналы после запуска бота
    for guild_id in os.listdir(path=data_path):
        guild_id = int(guild_id)
        if canals_txt.get(guild_id) is not None:
            guild_path = os.sep.join([data_path, str(guild_id)])

            canal_txt_copy = copy.copy(canals_txt[int(guild_id)])
            for canal in canals_txt[int(guild_id)]:
                main_text_canal = canal.split(':')[0]
                created_voice_canal = canal.split(':')[1]
                created_voice_canal_admin = canal.split(':')[2].replace('\n', '')
                channel = bot.get_channel(int(created_voice_canal))
                if channel is None:
                    canal_txt_copy.remove(canal)
                    # logging.info(f"canals_txt_befor = \n{canals_txt}")
                    with open(os.sep.join([guild_path, 'canals.txt']), 'w') as f_in:
                        for canal_to in canal_txt_copy:
                            f_in.write(canal_to + '\n')
                else:
                    members_id = []
                    for member in channel.members:
                        members_id.append(str(member.id))
                    if len(members_id) == 0:
                        try:
                            await channel.delete()
                        except discord.errors.NotFound as exc:
                            print(f"try_in: await member.move_to(voice_channel) 126_line\n"
                                  f"guild_id: {guild_id}\n"
                                  f"voice_channel_id: {channel.id}\n"
                                  f"error =>\n"
                                  f"{exc}\n"
                                  f"{'-' * 16}")
                        canal_txt_copy.remove(canal)
                        with open(os.sep.join([guild_path, 'canals.txt']), 'w') as f_in:
                            for canal_to in canal_txt_copy:
                                f_in.write(canal_to + '\n')
                    elif created_voice_canal_admin not in members_id:
                        result = f"{main_text_canal}:{created_voice_canal}:{members_id[0]}"
                        canal_txt_copy[canal_txt_copy.index(canal)] = result
                        with open(os.sep.join([guild_path, 'canals.txt']), 'w') as f_in:
                            for canal_to in canal_txt_copy:
                                f_in.write(canal_to + '\n')
            canals_txt[int(guild_id)] = copy.copy(canal_txt_copy)


update_varns()


@bot.event
async def on_ready():
    await update_messages()
    await update_voice_canals()

    print(main_canals_json)
    print(canals_txt)
    print(f'We have logged in as {bot.user}')


@bot.command()
async def reg(ctx):
    global data_path
    global main_canals_json
    global canals_txt

    try:
        if not ctx.message.author.guild_permissions.administrator:
            return
    except AttributeError:
        embed = discord.Embed(
            title="Я не работаю с личными сообщениями",
            description=f"Если есть предложения или Вопросы, пишите ему: "
                        f"[yunikeil](https://discordapp.com/users/286914074422280194/)"
        )
        await ctx.send(embed=embed)
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
            global canals_txt
            global main_canals_json

            guild_id = ctx.guild.id
            guild_path = os.sep.join([data_path, str(guild_id)])
            if str(guild_id) not in os.listdir(path=data_path):
                os.mkdir(path=guild_path)
                open(os.sep.join([guild_path, 'logs.log']), "x").close()
                open(os.sep.join([guild_path, 'logs_errors.log']), "x").close()
                main_canals = open(os.sep.join([guild_path, 'main_canals.json']), "x")
                main_canals.write(json.dumps(main_canal_data))
                main_canals.close()
                open(os.sep.join([guild_path, 'canals.txt']), "x").close()
                open(os.sep.join([guild_path, 'locales.txt']), "x").close()
                canals_txt[int(guild_id)] = []
            else:
                with open(os.sep.join([guild_path, 'main_canals.json'])) as file:
                    main_canal_json_to_delete = json.load(file)
                    for data_in_mcj in main_canal_json_to_delete:
                        to_delete_channel = bot.get_channel(int(data_in_mcj))
                        await to_delete_channel.purge(limit=10, check=lambda message: message.author.id == bot_id)
                main_canals = open(os.sep.join([guild_path, 'main_canals.json']), "w")
                main_canals.write(json.dumps(main_canal_data))
                main_canals.close()

            # Функция отправки сообщений начальных
            main_canals_json.append(main_canal_data)
            for data_mcd in main_canal_data.items():
                text_channel = data_mcd[0]
                voice_channels = data_mcd[1]
                voice_channels_string = ""
                for voice_channel in voice_channels:
                    voice_channels_string = voice_channels_string + f"><#{voice_channel}>\n"
                embed = discord.Embed(
                    title="War Thunder Voice",
                    colour=discord.Colour.red(),
                    description=f"Chat for management:\n"
                                f"<#{text_channel}>\n"
                                f"Voice channels:\n"
                                f"{voice_channels_string}"
                )
                embed.set_image(url='https://media.discordapp.net/attachments/1039227923980353539/'
                                    '1044481856277585950/maxresdefault_1.jpg?width=960&height=540')
                # embed.set_thumbnail(url='https://memepedia.ru/wp-content/uploads/2018/08/dlydryywsaa1jp8-768x576.jpg')
                embed.set_footer(text='© WTServer 2022')

                voice_control_settings = bot.get_channel(int(text_channel))
                await voice_control_settings.send(embed=embed, view=VoiceButtons(language=None))
                # update_varns()

            embed = discord.Embed(
                title="Мастер настройки voice_bot",
                description=f"Настройки сохранены."
            )
            try:
                await interaction.response.edit_message(embed=embed, view=None)
            except discord.errors.NotFound as exc:
                print(f"mb this is purge:\n"
                      f"{exc}\n"
                      f"{'-' * 16}")

        embed = discord.Embed(
            title="Мастер настройки voice_bot",
            description=f"Следующим шагом вы сохраните настройки в файл.\n"
                        f"При сохранении все записанные текстовые чаты очистятся,\n"
                        f"в них отошлются управляющие сообщения."
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

        classView = discord.ui.View()
        classView.timeout = None
        await interaction.response.edit_message(
            embed=embed,
            view=classView
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
                        embed_description = "Вы выбрали такие Voice channels:"
                    voice_canals_string = ""
                    for voice_canal in voice_canals:
                        voice_canals_string = voice_canals_string + f"<#{voice_canal}>\n"

                    after_id_input_embed = discord.Embed(
                        title="Мастер настройки voice_bot",
                        description=f"{embed_description}\n"
                                    f"{voice_canals_string}"
                    )
                    classView = discord.ui.View()
                    classView.timeout = None
                    await interaction.response.edit_message(
                        embed=after_id_input_embed,
                        view=classView
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

        classView = discord.ui.View()
        classView.timeout = None
        await interaction.response.edit_message(
            embed=start_settings_button_callback_embed,
            view=classView
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
                    classView = discord.ui.View()
                    classView.timeout = None
                    await interaction.response.edit_message(
                        embed=after_id_input_embed,
                        view=classView
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

        classView = discord.ui.View()
        classView.timeout = None
        await interaction.response.edit_message(
            embed=start_settings_embed,
            view=classView
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

    settings_reset_button = discord.ui.Button(
        style=discord.ButtonStyle.danger,
        label="Прервать настройку",
        row=2
    )
    settings_reset_button.callback = settings_reset_callback

    classView = discord.ui.View()
    classView.timeout = None
    await ctx.send(embed=embed, view=classView
                   .add_item(item=start_settings_button)
                   .add_item(item=settings_reset_button))


@bot.command()
async def info(ctx):
    global data_path

    try:
        if not ctx.message.author.guild_permissions.administrator:
            return
    except AttributeError:
        embed = discord.Embed(
            title="Я не работаю с личными сообщениями",
            description=f"Если есть предложения или Вопросы, пишите ему: "
                        f"[yunikeil](https://discordapp.com/users/286914074422280194/)"
        )
        await ctx.send(embed=embed)
        return

    guild_id = ctx.guild.id
    guild_path = os.sep.join([data_path, str(guild_id)])
    if str(guild_id) in os.listdir(path=data_path):
        with open(os.sep.join([guild_path, 'main_canals.json'])) as json_file:
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
    global data_path
    global main_canals_json

    try:
        if not ctx.message.author.guild_permissions.administrator:
            return
    except AttributeError:
        embed = discord.Embed(
            title="Я не работаю с личными сообщениями",
            description=f"Если есть предложения или Вопросы, пишите ему: "
                        f"[yunikeil](https://discordapp.com/users/286914074422280194/)"
        )
        await ctx.send(embed=embed)
        return

    async def reset_settings_button_callback(interaction):
        global main_canals_json

        guild_id = interaction.guild.id
        guild_path = os.sep.join([data_path, str(guild_id)])
        if str(guild_id) in os.listdir(path=data_path):
            with open(os.sep.join([guild_path, 'main_canals.json'])) as file:
                main_canal_json_to_delete = json.load(file)
            shutil.rmtree(guild_path)

            # Зачищает переменную от управляющих каналов.
            text_reset_channels = []
            deleted_channels_string = ""
            main_canals_json_copy = copy.copy(main_canals_json)
            for main_canal_json in main_canals_json:
                if main_canal_json == main_canal_json_to_delete:
                    for data_in_mcj in main_canal_json:
                        text_reset_channels.append(data_in_mcj)
                        text_reset_channel = bot.get_channel(int(data_in_mcj))
                        """ Посмотреть возможность удаления только сообщения с командами message.id in messages
                        Файл messages будет храниться в дата и содержать идшники сообщения с командами
                        По факту же можно просто при каждом обновлении управляющего сообщения отсылать всю инфу заново
                        Или написать инфу от лица админов..
                        Также можно сохранять идшники сообщенией в базу, и редачить уже их"""
                        await text_reset_channel.purge(limit=10, check=lambda message: message.author.id == bot_id)
                        deleted_channels_string = deleted_channels_string + f"<#{data_in_mcj}>\n"
                    main_canals_json_copy.remove(main_canal_json_to_delete)
            main_canals_json = copy.copy(main_canals_json_copy)

            embed = discord.Embed(
                title="Сброс настроек voice_bot",
                description=f"Сброс выполнен.\nИспользуйте >reg  для повторной авторизации каналов. \n"
                            f"Каналы, которых коснулись изменения:\n{deleted_channels_string}"
            )
            # if str(ctx.channel.id) not in text_reset_channels:
            #   await interaction.response.edit_message(embed=embed, view=None)  # закостылил, тут ошибка была
            if str(ctx.channel.id) not in text_reset_channels:
                await ctx.channel.purge(limit=1, check=lambda message: message.author.id == bot_id)
            await ctx.send(embed=embed)

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


class VoiceButtons(discord.ui.View):
    global main_canals_json
    global canals_txt
    global data_path
    global bot_id

    class HumanToKickSelect(discord.ui.Select):
        def __init__(self, user_voice_channel_id):
            # time_out устананавливается в классе View(discord.ui.View) в функции вызова.
            self.user_voice_channel_id = user_voice_channel_id
            self.members_on_create = bot.get_channel(self.user_voice_channel_id).members
            options = []
            for member in self.members_on_create:
                options.append(
                    discord.SelectOption(label=f"{member.name}", value=f"{member}")
                )
            super().__init__(placeholder="People in the channel:", max_values=1, min_values=1, options=options)

        async def callback(self, interaction: discord.Interaction):
            if bot.get_channel(self.user_voice_channel_id) is None:
                await interaction.response.send_message("The channel is empty, or does not exist", ephemeral=True)
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
                        # Функционал для запрета этому пользователю входить в канал
                        async def deny_entry_callback(interaction):
                            try:
                                await bot.get_channel(self.user_voice_channel_id).set_permissions(member, connect=False)
                                await interaction.response.send_message(f"The ban is set for: <@{member.id}>",
                                                                        ephemeral=True)
                            except AttributeError as ex:
                                await interaction.response.send_message(f"You may have chosen a non-existent channel..",
                                                                        ephemeral=True)

                        deny_entry_button = discord.ui.Button(
                            style=discord.ButtonStyle.gray,
                            label="click me to ban this user from logging in"
                        )
                        deny_entry_button.callback = deny_entry_callback
                        human_in_canal = True
                        await member.move_to(None)
                        await member.move_to(None)
                        await interaction.response.send_message("The person has been removed from the channel.",
                                                                view=discord.ui.View().add_item(item=deny_entry_button),
                                                                ephemeral=True)
                if not human_in_canal: await interaction.response.send_message(
                    "This person is not in the channel.", ephemeral=True)
            else:
                await interaction.response.send_message(
                    "You are outside the channel you are trying to control.", ephemeral=True)

    """class SelectLanguageSelect(discord.ui.Select):
        def __init__(self, interaction_obj):
            # time_out устананавливается в классе View(discord.ui.View) в функции вызова.
            self.interaction_obj = interaction_obj
            options = [discord.SelectOption(label=f"ru", value=f"RU"),
                       discord.SelectOption(label=f"en", value=f"EN")]
            super().__init__(placeholder="Languages: ", max_values=1, min_values=1, options=options)

        async def callback(self, interaction: discord.Interaction):
            # смена языка
            # выключение кнопки в конце
            # проверка на админа
            ## 89 line
            pass"""

    class LimitButtonModal(discord.ui.Modal, title='Limit of people'):
        def __init__(self, user_voice_channel_id, timeout=180):
            super().__init__(timeout=timeout)
            self.user_voice_channel_id = user_voice_channel_id

        limit = discord.ui.TextInput(
            label='Limit',
            placeholder='Enter the limit of people...',
            min_length=1,
            max_length=2,
            required=False
        )

        async def on_submit(self, interaction: discord.Interaction):
            voice_channel = bot.get_channel(self.user_voice_channel_id)
            await voice_channel.edit(user_limit=self.limit.value)
            await interaction.response.send_message(
                content=f"The limit of people has been changed to: {self.limit}",
                ephemeral=True
            )

        async def on_error(self, interaction: discord.Interaction, error):
            # Добавить сюда логгер
            pass

    class DenyEntryButtonModal(discord.ui.Modal, title='Deny entry'):
        def __init__(self, user_voice_channel_id, timeout=180):
            super().__init__(timeout=timeout)
            self.user_voice_channel_id = user_voice_channel_id

        deny_user = discord.ui.TextInput(
            label='Deny entry',
            placeholder='Enter people id...',
            min_length=5,
            max_length=20,
            required=False
        )

        async def on_submit(self, interaction: discord.Interaction):
            voice_channel = bot.get_channel(self.user_voice_channel_id)
            try:
                await bot.get_channel(self.user_voice_channel_id)\
                    .set_permissions(bot.get_user(int(self.deny_user.value)), connect=False)
                await interaction.response.send_message(f"The ban is set for: <@{self.deny_user.value}>",
                                                        ephemeral=True)
            except AttributeError as ex:
                await interaction.response.send_message(f"You may have chosen a non-existent channel..",
                                                        ephemeral=True)

        async def on_error(self, interaction: discord.Interaction, error):
            await interaction.response.send_message(f"You may have chosen a non-existent channel..",
                                                    ephemeral=True)


    """class RenameButtonModal(discord.ui.Modal, title='Rename'):
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
            pass"""

    def __init__(self, language):
        super().__init__()
        self.language = language
        self.timeout = None

    @staticmethod
    async def checkCanal(interaction):
        guild_id = interaction.guild.id

        """# Тут лежит прежняя версия типо проверки
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
        """

        # print("channel of button id:", interaction.channel.id)  # текстовый в котором нажата кнопка
        # print("voice people channel id:", interaction.user.voice.channel.id)  # в каком сидит пользователь
        # Находится в той же папке каналов
        if interaction is not None:
            try:
                if str(interaction.channel.category) == str(interaction.user.voice.channel.category):
                    # Первая проверка на то является ли человек внутри канала который создал сервер
                    # Вторая проверка на то является ли человек админом голосового на котором сидит
                    if str(f"{interaction.channel.id}:"
                           f"{interaction.user.voice.channel.id}:"
                           f"{interaction.user.id}") in canals_txt[int(guild_id)]:
                        return True, interaction.user.voice.channel.id
                    # Третья проверка на то откуда идёт вызов из текстового который управляет или нет
                    #  частично покрывается нулевой проверкой. (если в группе несколько управляющих, работать будет криво)
                    # elif str(interaction.channel.id) in str(main_canals_json):
                    #    print("Всё ок")
                    #    pass
                    else:
                        await interaction.response.send_message(
                            content=f"Probably, the bot does not control the channel in which "
                                    f" you are. Or you are not the administrator of this channel.",
                            ephemeral=True
                        )
                        return False, None
                else:
                    # Находится в другой папке каналов
                    await interaction.response.send_message(
                        content=f"You are outside of the active channel group, "
                                f" or the bot's area of operation.",
                        ephemeral=True
                    )
                    return False, None
            except AttributeError:
                await interaction.response.send_message(
                    content=f"You are outside the active channel group, "
                            f" or the bot's coverage area.",
                    ephemeral=True
                )
                return False, None

    @discord.ui.button(label="Limit of people", style=discord.ButtonStyle.primary, row=1)
    async def limit_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        isBool, user_voice_channel_id = await self.checkCanal(interaction)
        if isBool:
            await interaction.response.send_modal(
                VoiceButtons.LimitButtonModal(user_voice_channel_id=user_voice_channel_id)
            )

    """@discord.ui.button(label="Переименовать", style=discord.ButtonStyle.primary, row=1)
    async def rename_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        isBool, user_voice_channel_id = await self.checkCanal(interaction)
        if isBool:
            await interaction.response.send_modal(
                VoiceButtons.RenameButtonModal(user_voice_channel_id=user_voice_channel_id)
            )"""

    @discord.ui.button(label="Close the channel", style=discord.ButtonStyle.primary, row=1)
    async def close_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        isBool, user_voice_channel_id = await self.checkCanal(interaction)
        if isBool:
            voice_channel = bot.get_channel(user_voice_channel_id)
            members = voice_channel.members
            await voice_channel.edit(user_limit=len(members))
            await interaction.response.send_message(
                content=f"The channel is closed.",
                ephemeral=True
            )

    @discord.ui.button(label="Open a channel", style=discord.ButtonStyle.primary, row=1)
    async def open_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        isBool, user_voice_channel_id = await self.checkCanal(interaction)
        if isBool:
            voice_channel = bot.get_channel(user_voice_channel_id)
            await voice_channel.edit(user_limit=0)
            await interaction.response.send_message(
                content=f"The channel is open.",
                ephemeral=True
            )

    @discord.ui.button(label="Expel a participant", style=discord.ButtonStyle.secondary, row=2)
    async def kick_out_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        isBool, user_voice_channel_id = await self.checkCanal(interaction)
        if isBool:
            class View(discord.ui.View):
                def __init__(self, *, timeout=180):
                    super().__init__(timeout=timeout)
                    self.add_item(VoiceButtons.HumanToKickSelect(user_voice_channel_id=user_voice_channel_id))

                async def on_timeout(self):
                    self.clear_items()

            await interaction.response.send_message(
                content="Select the participant you want to kick: ",
                ephemeral=True,
                view=View()
            )

    @discord.ui.button(label="Deny entry", style=discord.ButtonStyle.gray, row=2)
    async def deny_entry(self, interaction: discord.Interaction, button: discord.ui.Button):
        isBool, user_voice_channel_id = await self.checkCanal(interaction)
        if isBool:
            await interaction.response.send_modal(
                VoiceButtons.DenyEntryButtonModal(user_voice_channel_id=user_voice_channel_id)
            )

    """@discord.ui.button(label="Language", style=discord.ButtonStyle.danger, row=2)
    async def test_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        if self.language is not None:
            ## Бдующий функционал который автоматические пересылает с готовым языком.
            return
        else:
            ## Чтоб это реализовать нужно полностью переписывать структуру VoiceButtons()!
            return"""

    """@discord.ui.button(label="test", style=discord.ButtonStyle.danger, row=2)
    async def test_button(self, interaction: discord.Interaction, button: discord.ui.Button):
        await interaction.response.send_message(
            content="test button!",
            ephemeral=True
        )"""


## Стоит добавить задержку между действиями хотя бы в 2 секунды.
@bot.event
async def on_voice_state_update(member, before, after):
    global main_canals_json
    global canals_txt
    global data_path
    global bot_id
    guild_path = os.sep.join([data_path, str(member.guild.id)])

    # Проверка на регистрацию гильдии...
    # if str(member.guild.id) in os.listdir(path=data_path):
    #    return

    # after использовать для вновь присоединившихся пользователей в управляющий голосовой.
    # также тут создаются каналы в canals_txt и canals.txt
    if after.channel is not None and str(member.guild.id) in os.listdir(path=data_path):
        for main_canal in main_canals_json:
            for data_server in main_canal.items():
                text_channel = data_server[0]
                voice_channels = data_server[1]
                try:
                    if str(after.channel.id) in voice_channels:
                        reference = bot.get_channel(after.channel.id)  # берем какой-нибудь канал за "основу"
                        smyles = ["❄", "🌨", "⛄", "😬", "🧤", "🏒", "⛸", "🧊", "⛷", "🏂", "🎿", "🛷", "🥶",
                                  "🎄", "🎁", "🎅"]
                        voice_channel = await member.guild.create_voice_channel(
                            name=f"{after.channel.name.replace('➕', '● ')} {random.choice(smyles)}",
                            # position=reference.position,  # создаём канал под "основой"
                            category=reference.category,  # в категории канала-"основы"
                            reason="voice_bot",  # (отображается в Audit Log)
                        )
                        await voice_channel.edit(sync_permissions=True)
                        back_res = f"{voice_channel.id}:{datetime.datetime.now().hour}-{datetime.datetime.now().minute}"
                        # Управляющий текстовый:Созданный голосовой:Админ
                        result = f"{text_channel}:{voice_channel.id}:{member.id}"
                        canals_txt[int(member.guild.id)].append(result)
                        with open('backCanals.txt', 'a') as f_in:
                            f_in.write(back_res + '\n')
                        with open(os.sep.join([guild_path, 'canals.txt']), 'a') as f_in:
                            f_in.write(result + '\n')
                        try:
                            await member.move_to(voice_channel)
                        except discord.errors.HTTPException as exc:
                            pass
                        await asyncio.sleep(5)
                        if bot.get_channel(voice_channel.id) is not None and len(voice_channel.members) == 0:
                            try:
                                await voice_channel.delete()
                            except Exception as exc:
                                pass
                            try:
                                canals_txt[int(member.guild.id)].remove(result)
                                with open(os.sep.join([guild_path, 'canals.txt']), 'w') as f_in:
                                    for canal_to in canals_txt[int(member.guild.id)]:
                                        f_in.write(canal_to + '\n')
                            except ValueError as exc:
                                pass
                except AttributeError as exc:
                    pass

    # before использовать для тех кто покидает канал созданный ботом.
    if before.channel is not None and canals_txt.get(int(member.guild.id)) is not None:
        for canal in canals_txt[int(member.guild.id)]:
            main_text_canal = canal.split(':')[0]
            created_voice_canal = canal.split(':')[1]
            created_voice_canal_admin = canal.split(':')[2].replace("\n", '')
            if str(before.channel.id) == created_voice_canal:
                # Две проверки
                # первая на то, что канал пустой, удалить канал
                # вторая на то, что ливнул админ, назначить нового админа
                # print(f"before: {before.channel.id} admin: {member.id}")
                try:
                    if len(before.channel.members) == 0:
                        try:
                            ch = bot.get_channel(int(created_voice_canal))
                            await ch.delete()
                        except discord.errors.NotFound as e:
                            print(created_voice_canal)
                            print(e)
                        # Не ставлю copy.copy() т.к физически не может быть больше одного канала.
                        # copy.copy() Не нужна, т.к канал может быть только один
                        try:
                            canals_txt[int(member.guild.id)].remove(canal)
                            with open(os.sep.join([guild_path, 'canals.txt']), 'w') as f_in:
                                for canal_to in canals_txt[int(member.guild.id)]:
                                    f_in.write(canal_to + '\n')
                        except:
                            pass
                    elif str(member.id) == str(created_voice_canal_admin) and member not in before.channel.members:
                        # тут лоигка назначения нового админа
                        result = f"{main_text_canal}:{created_voice_canal}:{before.channel.members[0].id}"
                        canals_txt[int(member.guild.id)][canals_txt[int(member.guild.id)].index(canal)] = result
                        with open(os.sep.join([guild_path, 'canals.txt']), 'w') as f_in:
                            for canal_to in canals_txt[int(member.guild.id)]:
                                f_in.write(canal_to + '\n')
                except FileNotFoundError as exc:
                    pass


@bot.command()
async def varn(ctx):
    print("123")
    try:
        if not ctx.message.author.guild_permissions.administrator:
            return
        await ctx.send(f"canals_txt = {canals_txt}")
    except AttributeError:
        embed = discord.Embed(
            title="Я не работаю с личными сообщениями",
            description=f"Если есть предложения или Вопросы, пишите ему: "
                        f"[yunikeil](https://discordapp.com/users/286914074422280194/)"
        )
        await ctx.send(embed=embed)
        return


"""@bot.command()
async def help(ctx):
    try:
        if not ctx.message.author.guild_permissions.administrator:
            return
    except AttributeError:
        embed = discord.Embed(
            title="Я не работаю с личными сообщениями",
            description=f"Если есть предложения или Вопросы, пишите ему: "
                        f"[yunikeil](https://discordapp.com/users/286914074422280194/)"
        )
        await ctx.send(embed=embed)
        return
    await ctx.send("None")"""


@bot.event
async def on_command_error(ctx, error):
    if isinstance(error, discord.ext.commands.CommandNotFound):
        return
    raise error


@bot.event
async def on_member_join(member):
    await asyncio.sleep(10 * 60)
    try:
        member = member
        guild = member.guild
        ru_role_id = configuration.ru_role_id
        en_role_id = configuration.en_role_id
        if member.get_role(ru_role_id) is None and member.get_role(en_role_id) is None:
            await member.add_roles(guild.get_role(ru_role_id))
            await member.add_roles(guild.get_role(en_role_id))
    except discord.errors.NotFound as e:
        pass


@bot.event
async def on_message(message):
    if 'https://discord.gg/' in message.content and not message.author.guild_permissions.administrator:
        roles_allowed = [discord.utils.find(lambda r: r.id == 954393422716879019, message.guild.roles),  # vip1
                         discord.utils.find(lambda r: r.id == 1007965606789783572, message.guild.roles),  # vip2
                         discord.utils.find(lambda r: r.id == 827202390682894358, message.guild.roles),  # deputy
                         discord.utils.find(lambda r: r.id == 812667192104583218, message.guild.roles)]  # head
        author_roles = message.author.roles
        for role_allowed in roles_allowed:
            if role_allowed in author_roles:
                return
        await message.delete()


## Добавить функцию, которая выводит созданные и удалённые в логи в дискорде, проверять гильдию на 69..

bot.run(configuration.token)

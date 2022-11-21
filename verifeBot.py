

"""
@bot.event
async def on_member_join(member):
    now = datetime.now()

    embed = discord.Embed(
        title='Добро пожаловать на "Тестовый сервер"!',
        description='',
        color=0x0000FF
    )
    embed.set_author(name=f'{member.name}#{member.discriminator}', icon_url=member.avatar_url)
    embed.set_footer(text=f'Ваш ID: {member.id} • {now.hour}:{now.minute}')

    await member.send(embed=embed)
    """
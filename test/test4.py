# This example requires the 'members' privileged intents

import discord


class MyClient(discord.Client):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        self.aman_id = 632552306398724106
        self.role_message_id = 1056154559833186384  # ID of the message that can be reacted to to add/remove a role.
        self.emoji_to_role = {
            discord.PartialEmoji(name='🎄'): 1056153147929804821,  # ID of the role associated with unicode emoji '🔴'.
        }

    async def on_raw_reaction_add(self, payload: discord.RawReactionActionEvent):
        """Gives a role based on a reaction emoji."""
        # удаляет реакции с моего сообщения от амантура
        channel = self.get_channel(payload.channel_id)
        msg = await channel.fetch_message(payload.message_id)
        if payload.user_id == self.aman_id and msg.author.id == 286914074422280194:
            for reaction in msg.reactions:
                await reaction.remove(self.get_user(self.aman_id))

        # Make sure that the message the user is reacting to is the one we care about.
        if payload.message_id != self.role_message_id:
            return

        guild = self.get_guild(payload.guild_id)
        if guild is None:
            # Check if we're still in the guild and it's cached.
            return

        try:
            role_id = self.emoji_to_role[payload.emoji]
        except KeyError:
            # If the emoji isn't the one we care about then exit as well.
            return

        role = guild.get_role(role_id)
        if role is None:
            # Make sure the role still exists and is valid.
            return

        try:
            # Finally, add the role.
            await payload.member.add_roles(role)
        except discord.HTTPException:
            # If we want to do something in case of errors we'd do it here.
            pass

    async def on_raw_reaction_remove(self, payload: discord.RawReactionActionEvent):
        """Removes a role based on a reaction emoji."""
        # Make sure that the message the user is reacting to is the one we care about.
        if payload.message_id != self.role_message_id:
            return

        guild = self.get_guild(payload.guild_id)
        if guild is None:
            # Check if we're still in the guild and it's cached.
            return

        try:
            role_id = self.emoji_to_role[payload.emoji]
        except KeyError:
            # If the emoji isn't the one we care about then exit as well.
            return

        role = guild.get_role(role_id)
        if role is None:
            # Make sure the role still exists and is valid.
            return

        # The payload for `on_raw_reaction_remove` does not provide `.member`
        # so we must get the member ourselves from the payload's `.user_id`.
        member = guild.get_member(payload.user_id)
        if member is None:
            # Make sure the member still exists and is valid.
            return

        try:
            # Finally, remove the role.
            await member.remove_roles(role)
        except discord.HTTPException:
            # If we want to do something in case of errors we'd do it here.
            pass

    async def on_raw_reaction_clear(self, payload: discord.RawReactionActionEvent):
        # удаление всех реакций с какого либо сообщения
        channel = self.get_channel(payload.channel_id)
        msg = await channel.fetch_message(payload.message_id)
        if msg.author.id == self.aman_id:
            await msg.add_reaction('🤡')

    async def on_message(self, message):
        if message.author.id == self.aman_id:
            await message.add_reaction('🤡')


intents = discord.Intents.default()
intents.members = True

client = MyClient(intents=intents)
client.run('MTA1NjE3Njk4MDA3NDE3MjQ3Nw.Gcvkgh.N5KKsjKLPilTcK6bC-PGwJ-VeUydSMo78rD8tY')
#client.run('MTAzNzQ3NzYzMzQxMzM0OTQwNg.GYfQls.5wj55LV8mcPWTcHyz--Ip8O48ngO9D_iExZAWE')
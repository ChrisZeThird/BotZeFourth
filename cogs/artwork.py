import discord
import json
import re

from discord.ext import commands
from utils.data import DiscordBot
from utils.misc import has_link


class Artwork(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot

    @commands.Cog.listener("on_message")
    async def thread_on_message(self, message):
        # If the file exists, load the data from the file
        with open('channels.json', 'r') as f:
            channels_dict = json.load(f)

        # Get the server ID
        if message.guild is not None:
            server_id = str(message.guild.id)
            if server_id in channels_dict:
                allowed_channels = channels_dict[server_id]
                if str(message.channel.id) in allowed_channels and len(message.attachments) > 0:
                    # Create a thread
                    thread = await message.create_thread(name=f"Artwork Discussion of {message.author.name}")
                    await thread.send(f"This is a thread for discussing the artwork sent by {message.author.mention}. "
                                      f"\nFeel free to share your thoughts!")
        else:
            pass

    @commands.Cog.listener("on_message")
    async def check_attachment(self, message):
        # We do not want the bot to reply to itself
        if message.author == self.bot.user:
            return

        # If the file exists, load the data from the file
        with open('channels.json', 'r') as f:
            channels_dict = json.load(f)

        # Get the server ID
        if message.guild is not None:
            server_id = str(message.guild.id)

            if server_id in channels_dict:
                allowed_channels = channels_dict[server_id]
                if str(message.channel.id) in allowed_channels:
                    if not message.author.guild_permissions.administrator:
                        if len(message.attachments) == 0 and not has_link(message):
                            # Delete the message
                            await message.delete()
                            # Send a message to the user discreetly
                            user = message.author
                            channel = await user.create_dm()
                            await channel.send(f"You cannot send messages without attachments in {message.channel.mention}.")

            else:
                pass
        else:
            pass


async def setup(bot):
    await bot.add_cog(Artwork(bot))
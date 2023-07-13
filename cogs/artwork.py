import discord
import json

from discord.ext import commands
from utils.data import DiscordBot


class Artwork(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot

    @commands.Cog.listener("on_message")
    async def thread_on_message(self, message):
        # If the file exists, load the data from the file
        with open('channels.json', 'r') as f:
            channels_dict = json.load(f)

        # Get the server ID
        server_id = str(message.guild.id)

        if server_id in channels_dict:
            allowed_channels = channels_dict[server_id]
            if str(message.channel.id) in allowed_channels and len(message.attachments) > 0:
                # Create a thread
                thread = await message.create_thread(name=f"Artwork Discussion of {message.author.name}")
                await thread.send(f"This is a thread for discussing the artwork sent by {message.author.mention}. "
                                  f"\nFeel free to share your thoughts!")

    @commands.Cog.listener("on_message")
    async def check_attachment(self, message):
        # If the file exists, load the data from the file
        with open('channels.json', 'r') as f:
            channels_dict = json.load(f)
        # Get the server ID
        server_id = str(message.guild.id)

        if server_id in channels_dict:
            allowed_channels = channels_dict[server_id]

            if str(message.channel.id) in allowed_channels and len(message.attachments) == 0 and not message.author.guild_permissions.administrator:
                # Delete the message
                await message.delete()
                # Send a message to the user discreetly
                user = message.author
                await user.send(f"You cannot send messages without attachments in {message.channel.mention}.")


async def setup(bot):
    await bot.add_cog(Artwork(bot))

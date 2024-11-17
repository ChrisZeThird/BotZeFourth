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
        try:
            # If the message is a DM or not in a guild, ignore it
            if message.guild is None:
                return

            # Load the channels data
            try:
                with open('channels.json', 'r') as f:
                    channels_dict = json.load(f)
            except FileNotFoundError:
                print("channels.json file not found.")
                return
            except json.JSONDecodeError:
                print("Error decoding channels.json file.")
                return

            server_id = str(message.guild.id)

            if server_id in channels_dict:
                allowed_channels = channels_dict[server_id]

                if (str(message.channel.id) in allowed_channels and
                    len(message.attachments) == 0 and
                    not message.author.guild_permissions.administrator):
                    try:
                        # Delete the message
                        await message.delete()
                        # Send a message to the user discreetly
                        await message.author.send(f"You cannot send messages without attachments in {message.channel.mention}.")
                    except discord.errors.NotFound:
                        print(f"Message {message.id} was already deleted.")
                    except discord.errors.Forbidden:
                        print(f"Bot doesn't have permission to delete message {message.id} or DM user {message.author.id}")

        except Exception as e:
            print(f"An error occurred in check_attachment: {str(e)}")


async def setup(bot):
    await bot.add_cog(Artwork(bot))

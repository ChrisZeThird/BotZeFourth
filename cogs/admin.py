import json
import os
import sqlite3

from utils import permissions
from utils.default import CustomContext
from discord.ext import commands
from utils.data import DiscordBot


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot

    @commands.hybrid_command(name='createdatabase', with_app_command=True)
    @commands.check(permissions.is_owner)
    async def createdatabase(self, ctx: CustomContext):
        """ Create a database for your server. You can either make it 'private' or 'public'."""
        # Get guild id
        guild_name = ctx.guild.name
        guild_id = str(ctx.guild.id)

        # Connect to sqlite database
        con = sqlite3.connect("database.db")
        cur = con.cursor()

        # Create database according to guild id
        cur.execute(f"CREATE TABLE guild_{guild_id} (author_name TEXT, author_id INTEGER, oc_name TEXT, oc_age INTEGER, oc_nationality TEXT, oc_gender TEXT, oc_sexuality TEXT, oc_universe TXT, oc_story TEXT, oc_picture, oc_colour)")
        # Commit changes
        con.commit()
        # Close cursor
        con.close()

        # Confirm database creation in text channel
        await ctx.send(f"Database for {guild_name} (id: {guild_id}) was successfully created")

    @commands.hybrid_command(name='addrole', with_app_command=True)
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx: CustomContext, role):
        """ Add roles allowed to use the bot"""
        # Check if the JSON file exists
        if not os.path.exists('roles.json'):
            open('roles.json', 'w').close()
        # If the file exists, load the data from the file
        with open('roles.json', 'r') as f:
            roles_dict = json.load(f)

        # Get the server ID
        server_id = str(ctx.guild.id)
        if server_id not in roles_dict:
            roles_dict[server_id] = []

        if role not in roles_dict[server_id]:
            roles_dict[server_id].append(role)

            # Save the data to the JSON file
            with open('roles.json', 'w') as f:
                json.dump(roles_dict, f)

            await ctx.send(f"**Following roles are now allowed to use BotZeFourth database system**: <@&{role}>")

        else:
            await ctx.send('**Role already allowed to use BotZeFourth database system.**')

    @commands.hybrid_command(name='removerole', with_app_command=True)
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx: CustomContext, roles):
        """ Remove roles allowed to use the bot"""
        # Check if the JSON file exists
        if not os.path.exists('roles.json'):
            await ctx.send("File to store authorized roles missing.")
            return

        # Load the data from the JSON file
        with open('roles.json', 'r') as f:
            roles_dict = json.load(f)

        # Get the server ID
        server_id = str(ctx.guild.id)
        if server_id not in roles_dict:
            await ctx.send("No roles have been added yet.")
            return

        # Save the data to the JSON file
        with open('roles.json', 'w') as f:
            json.dump(roles_dict, f)

        await ctx.send(
            f"**Following roles have been removed from the list of roles allowed to use BotZeFourth database system**: "
            f"{', '.join(f'<@&{role}>' for role in roles)}")

    @commands.hybrid_command(name='addchannel', with_app_command=True)
    @commands.has_permissions(manage_channels=True)
    async def addchannel(self, ctx: CustomContext, channel_id):
        # Check if the JSON file exists
        if not os.path.exists('channels.json'):
            open('channels.json', 'w').close()
            return

        # If the file exists, load the data from the file
        with open('channels.json', 'r') as f:
            channels_dict = json.load(f)

        # Get the server ID
        server_id = str(ctx.guild.id)
        # Get channel object to ensure user input an actual channel
        channel = self.bot.get_channel(int(channel_id))

        if channel:
            # Make sure the dictionary is set up before adding a channel
            if server_id not in channels_dict:
                channels_dict[server_id] = []

            if channel_id not in channels_dict[server_id]:
                channels_dict[server_id].append(channel_id)

                # Save the data to the JSON file
                with open('channels.json', 'w') as f:
                    json.dump(channels_dict, f)

                await ctx.send(f"Channel {channel.mention} has been added.")

        else:
            await ctx.send("Invalid channel ID.")


async def setup(bot):
    await bot.add_cog(Admin(bot))

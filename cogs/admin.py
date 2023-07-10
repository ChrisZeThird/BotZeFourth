import discord
import json
import os
import sqlite3

from io import BytesIO
from utils import default, permissions
from utils.default import CustomContext
from discord.ext import commands
from utils.data import DiscordBot


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot

    @commands.command()
    @commands.check(permissions.is_owner)
    async def createdatabase(self, ctx: CustomContext):
        """ Create a database for your server. You can either make it 'private' or 'public'."""
        # Get guild id
        guild_name = ctx.guild.name
        guild_id = ctx.guild.id

        # Connect to sqlite database
        con = sqlite3.connect("database.db")
        cur = con.cursor()

        # Create database according to guild id
        cur.execute(f"CREATE TABLE guild_{guild_id} (author_name TEXT, author_id INTEGER, oc_name TEXT, oc_age INT, oc_gender TXT, oc_story TXT, oc_universe TXT)")
        # Commit changes
        con.commit()
        # Close cursor
        con.close()

        # Confirm database creation in text channel
        await ctx.send(f"Database for {guild_name} (id: {guild_id}) was successfully created")

    @commands.command()
    @commands.check(permissions.is_owner)
    async def addrole(self, ctx: CustomContext, *roles):
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
            roles_dict[server_id] = [role for role in roles]
        else:
            roles_dict[server_id].extend([role for role in roles if role not in roles_dict[server_id]])

        # Save the data to the JSON file
        with open('roles.json', 'w') as f:
            json.dump(roles_dict, f)

        await ctx.send(f"**Following roles are now allowed to use BotZeFourth database system**: {', '.join(f'<@&{role}>' for role in roles)}")

    @commands.command()
    @commands.check(permissions.is_owner)
    async def removerole(self, ctx: CustomContext, *roles):
        """ Remove roles allowed to use the bot"""
        # Check if the JSON file exists
        if not os.path.exists('roles.json'):
            await ctx.send("No roles have been added yet.")
            return

        # Load the data from the JSON file
        with open('roles.json', 'r') as f:
            roles_dict = json.load(f)

        # Get the server ID
        server_id = str(ctx.guild.id)
        if server_id not in roles_dict:
            await ctx.send("No roles have been added yet.")
            return

        # Remove the roles from the list of roles allowed to use the bot
        for role in roles:
            print(role)
            if role in roles_dict[server_id]:
                print(roles_dict)
                roles_dict[server_id].remove(role)
                print(roles_dict)

        # Save the data to the JSON file
        with open('roles.json', 'w') as f:
            json.dump(roles_dict, f)

        await ctx.send(
            f"**Following roles have been removed from the list of roles allowed to use BotZeFourth database system**: "
            f"{', '.join(f'<@&{role}>' for role in roles)}")


async def setup(bot):
    await bot.add_cog(Admin(bot))

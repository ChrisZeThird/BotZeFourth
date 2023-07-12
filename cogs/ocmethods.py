import aiosqlite
import asyncio
import discord
import json
import os


from discord.ext import commands
from discord.ui import Select, View
from interactions import autodefer
from postgreslite import PostgresLite
from utils.data import DiscordBot
from utils.default import CustomContext
from utils.misc import extract_role_ids
from utils.picker import ColorPicker
from typing import Optional


class OCmanager(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot
        # Check if the JSON file exists
        if not os.path.exists('roles.json'):
            open('roles.json', 'w').close()
        # If the file exists, load the data from the file
        with open('roles.json', 'r') as f:
            self.roles_dict = json.load(f)

    @commands.hybrid_command(name='addoc', with_app_command=True)
    # @commands.cooldown(rate=1, per=60, type=commands.BucketType.user)
    async def addoc(self, ctx, name, age, nationality, gender, sexuality, universe, desc, picture: discord.Attachment):
        """ Add OC to the database with respect to user and guild id """
        # await ctx.defer()  # defer response, now we have 15 minutes to reply
        # Get guild and user roles
        guild_id = str(ctx.guild.id)
        user_roles = extract_role_ids(ctx.message.author.roles)  # roles formatting needed to only keep the actual id
        try:
            # Check if permissions have been set for the server
            roles_list = self.roles_dict[guild_id]
            # Check is user is allowed to use the database
            if any(str(role) in roles_list for role in user_roles):
                user_id = ctx.message.author.id
                user_name = ctx.message.author.name

                view = ColorPicker()
                await ctx.send(view=view)
                await view.wait()

                colour = view.colour[0]

                await ctx.send(f'You have picked {colour} for your OC!')

                print(await self.bot.pool.execute("""
                    INSERT INTO users (
                          user_id, guild_id, user_name, oc_name, oc_age, oc_nationality,
                          oc_gender, oc_sexuality, oc_universe, oc_story, oc_picture, oc_colour
                        )  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) 
                    """, user_id, guild_id, user_name, name, age, nationality, gender, sexuality, universe, desc, picture.url, colour)
                      )
                await ctx.send(f'Character successfully added for <@{user_id}>!')

            else:
                await ctx.send("**If you think you should be able to add a character to the database, contact your local admins.**")

        except KeyError:
            await ctx.send("**Please set the authorized roles first with `addrole` before adding an OC.**")

    @commands.hybrid_command(name='deleteoc', with_app_command=True)
    async def deleteoc(self, ctx: CustomContext):
        """ Delete an oc from the database """
        # Get guild and user roles
        guild_id = str(ctx.guild.id)
        user_roles = extract_role_ids(ctx.message.author.roles)  # roles formatting needed to only keep the actual id
        try:
            # Check if permissions have been set for the server
            roles_list = self.roles_dict[guild_id]
            # Check is user is allowed to use the database
            if any(role in roles_list for role in user_roles):
                user_id = ctx.message.author.id
                result = self.bot.pool.execute('SELECT * FROM users WHERE author_id = ?', user_id)
                row = result.fetchone()

                if row is not None:
                    def check(m):
                        return m.author == ctx.author

                    await ctx.send("Enter the name of the character to delete: ")
                    oc_name = await self.bot.wait_for('message', check=check, timeout=60)

                    self.bot.pool.execute('DELETE FROM users WHERE author_id = ? AND oc_name = ?', user_id, oc_name)

                    await ctx.send(f'Character successfully deleted for <@{user_id}>!')

                else:
                    await ctx.send(f'No character found for {ctx.message.author} (id:{user_id})')

        except KeyError:
            await ctx.send("**Please set the authorized roles first with `addrole` before deleting an OC.**")

    @commands.hybrid_command(name='listoc', with_app_command=True)
    async def listoc(self, ctx: CustomContext, artist):
        """ List all oc of an artist, by default should list ocs at random if the user is not in the database """
        result = self.bot.pool.execute('SELECT oc_name FROM users WHERE author_id = ?', ctx.author.id)
        rows = result.fetchall()

        if rows:
            # User is in the database and has OCs
            oc_list = [row[0] for row in rows]  # Extract the oc_name values from the rows
            oc_list_str = "\n".join(oc_list)  # Join the oc_list elements with newlines
            await ctx.send(f"OCs for {ctx.author.name}:\n{oc_list_str}")
        else:
            # User is not in the database or does not have OCs
            await ctx.send("You do not have any OCs. Sending OCs of a random user.")
            # Retrieve a random author_id from the database
            result = self.bot.pool.execute('SELECT author_id FROM users ORDER BY RANDOM() LIMIT 1')
            row = result.fetchone()
            oc_list = [row[0] for row in rows]  # Extract the oc_name values from the rows
            oc_list_str = "\n".join(oc_list)  # Join the oc_list elements with newlines
            await ctx.send(f"OCs of artist:\n{oc_list_str}")

    # @commands.hybrid_command(name='ocinfo', with_app_command=True)
    # async def ocinfo(self, ctx: CustomContext, oc_name):
    #     """ Gives the information sheet of an OC """


async def setup(bot):
    await bot.add_cog(OCmanager(bot))

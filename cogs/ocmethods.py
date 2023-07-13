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
from utils.embed import init_embed
from utils.misc import extract_role_ids
from utils.picker import ColorPicker, OCModifier
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
        # print(user_roles)
        try:
            # Check if permissions have been set for the server
            roles_list = self.roles_dict[guild_id]
            # print(roles_list)
            # Check is user is allowed to use the database
            if any(str(role) in roles_list for role in user_roles):
                user_id = ctx.message.author.id
                user_name = ctx.message.author.name

                view = ColorPicker(bot=self.bot)
                await ctx.send(view=view)
                await view.wait()

                colour = view.colour
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
            # Check if user is allowed to use the database
            if any(role in roles_list for role in user_roles):
                user_id = ctx.message.author.id
                result = await self.bot.pool.fetch('SELECT * FROM users WHERE user_id = ?', user_id)

                if result is not None:
                    def check(m):
                        return m.author == ctx.author

                    # User is in the database and has OCs
                    oc_list = [row['oc_name'] for row in result]  # Extract the oc_name values from the rows
                    oc_list_str = "\n".join(oc_list)  # Join the oc_list elements with newlines
                    await ctx.send(f"# :clipboard: List of your OCs:\n**{oc_list_str}**")

                    # Ask user which OC to delete
                    await ctx.send("Enter the name of the character to delete: ")
                    oc_name = await self.bot.wait_for('message', check=check, timeout=60)
                    # Get the content of the message
                    oc_name_content = oc_name.content

                    if oc_name_content in oc_list:
                        await self.bot.pool.execute('DELETE FROM users WHERE user_id = ? AND oc_name = ?', user_id,
                                                    oc_name_content)
                        await ctx.send(f'Character {oc_name_content} successfully deleted for <@{user_id}>!')
                    else:
                        await ctx.send(f'Invalid OC name. Please enter a valid name from the list.')

                else:
                    await ctx.send(f'No character found for {ctx.message.author} (id:{user_id})')

        except KeyError:
            await ctx.send("**Please set the authorized roles first with `addrole` before deleting an OC.**")

    @commands.hybrid_command(name='modifyoc', with_app_command=True)
    async def modifyoc(self, ctx, oc_name: str):
        """ Modify OC in the database with respect to user and guild id """
        # Get guild and user roles
        guild_id = str(ctx.guild.id)
        user_roles = extract_role_ids(ctx.message.author.roles)

        try:
            # Check if permissions have been set for the server
            roles_list = self.roles_dict[guild_id]

            # Check if user is allowed to use the database
            if any(str(role) in roles_list for role in user_roles):
                # Get the OC from the database
                oc = await self.bot.pool.fetch("""
                        SELECT * FROM users WHERE user_id = ? AND guild_id = ? AND oc_name = ?
                    """, ctx.message.author.id, guild_id, oc_name)
                # Check if the OC exists
                if not oc:
                    await ctx.send(f"No OC found with the name {oc_name}.")
                    return

                # Create an instance of the OCModifier view
                oc_modifier = OCModifier(self.bot)

                # Wait for the user to make their selections
                await ctx.send("Select fields to modify:", view=oc_modifier)
                await oc_modifier.wait()

                # Get the modified fields and update the OC in the database
                new_values = oc_modifier.modified_fields
                set_clause = ', '.join([f'{field} = ?' for field in new_values.keys()])
                values = list(new_values.values()) + [ctx.message.author.id, guild_id, oc_name]
                await self.bot.pool.execute(f"""UPDATE users SET {set_clause} WHERE user_id = ? AND guild_id = ? AND oc_name = ?
                    """, *values)

                await ctx.send(f'OC called {oc_name} successfully modified!')

            else:
                await ctx.send(
                    "**If you think you should be able to modify an OC in the database, contact your local admins.**")
        except KeyError:
            await ctx.send("**Please set the authorized roles first with `addrole` before deleting an OC.**")

    @commands.hybrid_command(name='listoc', with_app_command=True)
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def listoc(self, ctx: CustomContext, artist_name):
        """ List all oc of an artist """
        rows = await self.bot.pool.fetch('SELECT oc_name FROM users WHERE user_name = ?', artist_name)

        if rows:
            # User is in the database and has OCs
            oc_list = [row['oc_name'] for row in rows]  # Extract the oc_name values from the rows
            oc_list_str = "\n".join(oc_list)  # Join the oc_list elements with newlines
            await ctx.send(f"# :clipboard: OCs for {artist_name}:\n**{oc_list_str}**")
        else:
            # User is not in the database or does not have OCs
            await ctx.send(f"{artist_name} do not have any OCs!")

    @commands.hybrid_command(name='listartist', with_app_command=True)
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def listartist(self, ctx: CustomContext):
        """ List all artists of a server """
        rows = await self.bot.pool.fetch('SELECT user_name FROM users WHERE guild_id = ?', ctx.guild.id)

        if rows:
            # User is in the database and has OCs
            artist_list = [row['user_name'] for row in rows]  # Extract the oc_name values from the rows
            artist_list_str = "\n".join(artist_list)  # Join the oc_list elements with newlines
            await ctx.send(f"# :clipboard: Artist with OCs:\n**{artist_list_str}**")
        else:
            # User is not in the database or does not have OCs
            await ctx.send(f"No artist has been found!")

    @commands.hybrid_command(name='randomoc', with_app_command=True)
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def randomoc(self, ctx: CustomContext):
        """ Send the description of a random selected OC """
        # Get sqlite row
        rows = await self.bot.pool.fetch('SELECT * FROM users WHERE guild_id = ? ORDER BY RANDOM() LIMIT 1', ctx.guild.id)

        # Store all information
        user_id = rows[0]['user_id']
        user_name = rows[0]['user_name']
        oc_age = rows[0]['oc_name']
        oc_nationality = rows[0]['oc_nationality']
        oc_gender = rows[0]['oc_gender']
        oc_sexuality = rows[0]['oc_sexuality']
        oc_universe = rows[0]['oc_universe']
        oc_story = rows[0]['oc_story']
        oc_picture = rows[0]['oc_picture']
        oc_color = int(rows[0]['oc_colour'][1:], 16)

        user = ctx.bot.get_user(user_id)
        avatar_url = user.avatar

        # Create embed
        embed = init_embed()
        embed.description = oc_story
        embed.colour = oc_color

        embed.set_field_at(0, name="Age", value=oc_age)
        embed.set_field_at(1, name="Nationality", value=oc_nationality)
        embed.set_field_at(2, name="Universe", value=oc_universe)
        embed.set_field_at(3, name="Gender", value=oc_gender)
        embed.set_field_at(4, name="Sexuality", value=oc_sexuality)

        embed.set_thumbnail(url=avatar_url)  # Artist avatar
        embed.set_image(url=oc_picture)  # OC illustration
        embed.set_footer(text=f"Author: {user_name}")  # Artist name at the bottom

        await ctx.send(embed=embed)

    @commands.hybrid_command(name='ocinfo', with_app_command=True)
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def ocinfo(self, ctx: CustomContext, artist_name, oc_name):
        """ Gives the information sheet of an OC """
        # Get sqlite row
        rows = await self.bot.pool.fetch('SELECT * FROM users WHERE guild_id = ? AND user_name = ? AND oc_name = ?',
                                         ctx.guild.id, artist_name, oc_name)
        print(rows)
        # Store all information
        user_id = rows[0]['user_id']
        user_name = rows[0]['user_name']
        oc_age = rows[0]['oc_name']
        oc_nationality = rows[0]['oc_nationality']
        oc_gender = rows[0]['oc_gender']
        oc_sexuality = rows[0]['oc_sexuality']
        oc_universe = rows[0]['oc_universe']
        oc_story = rows[0]['oc_story']
        oc_picture = rows[0]['oc_picture']
        oc_color = int(rows[0]['oc_colour'][1:], 16)

        user = ctx.bot.get_user(user_id)
        avatar_url = user.avatar

        # Create embed
        embed = init_embed()
        embed.description = oc_story
        embed.colour = oc_color

        embed.set_field_at(0, name="Age", value=oc_age)
        embed.set_field_at(1, name="Nationality", value=oc_nationality)
        embed.set_field_at(2, name="Universe", value=oc_universe)
        embed.set_field_at(3, name="Gender", value=oc_gender)
        embed.set_field_at(4, name="Sexuality", value=oc_sexuality)

        embed.set_thumbnail(url=avatar_url)  # Artist avatar
        embed.set_image(url=oc_picture)  # OC illustration
        embed.set_footer(text=f"Author: {user_name}")  # Artist name at the bottom

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(OCmanager(bot))

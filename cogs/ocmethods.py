import asyncio
import discord
import json
import os

from discord.ext import commands
from utils.data import DiscordBot
from utils.default import CustomContext
from utils.embed import init_embed
from utils.misc import extract_role_ids
from utils.picker import ColorPicker, OCModifier


class OCmanager(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot
        # Check if the JSON file exists
        if not os.path.exists('roles.json'):
            open('roles.json', 'w').close()
        # If the file exists, load the data from the file
        with open('roles.json', 'r') as f:
            self.roles_dict = json.load(f)

    @commands.hybrid_command(name='ocadd', with_app_command=True)
    # @commands.cooldown(rate=1, per=60, type=commands.BucketType.user)
    async def ocadd(self, ctx, name, age, nationality, gender, sexuality, universe, desc, picture: discord.Attachment):
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
                if picture.content_type in ['image/png', 'image/jpeg']:
                    user_id = ctx.message.author.id
                    user_name = ctx.message.author.name

                    view = ColorPicker(bot=self.bot)
                    await ctx.send(view=view)
                    await view.wait()

                    colour = view.colour
                    await ctx.send(f'You have picked {colour} for your OC!')

                    oc_picture = await picture.read()
                    print(await self.bot.pool.execute("""
                        INSERT INTO characters (
                              user_id, guild_id, user_name, oc_name, oc_age, oc_nationality,
                              oc_gender, oc_sexuality, oc_universe, oc_story, oc_picture, oc_colour
                            )  VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?) 
                        """, user_id, guild_id, user_name, name, age, nationality, gender, sexuality, universe, desc, oc_picture, colour)
                          )
                    await ctx.send(f'Character successfully added for <@{user_id}>!')
                else:
                    # The attachment is not a PNG or JPEG file
                    await ctx.send("Please attach a **PNG** or **JPEG** file.")
            else:
                await ctx.send("**If you think you should be able to add a character to the database, contact your local admins.**")

        except KeyError:
            await ctx.send("**Please set the authorized roles first with `addrole` before adding an OC.**")

    @commands.hybrid_command(name='ocdelete', with_app_command=True)
    async def ocdelete(self, ctx: CustomContext):
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
                result = await self.bot.pool.fetch('SELECT * FROM characters WHERE user_id = ?', user_id)

                if result is not None:
                    def check(m):
                        return m.author == ctx.author

                    # List the OC(s)
                    oc_list = [row['oc_name'] for row in result]  # Extract the oc_name values from the rows
                    oc_list_str = "\n".join(oc_list)  # Join the oc_list elements with newlines

                    # Ask what OC name to delete
                    await ctx.send(f"# :broom: Enter the name of the character to delete from the following list:\n**{oc_list_str}**")
                    try:
                        oc_name = await self.bot.wait_for('message', check=check, timeout=15)
                        await self.bot.pool.execute('DELETE FROM characters WHERE user_id = ? AND oc_name = ?', user_id,
                                                    oc_name.content)

                        await ctx.send(f'Character successfully deleted for <@{user_id}>!')

                    except asyncio.TimeoutError:
                        await ctx.send("You took too long. No OC was deleted.")

                else:
                    await ctx.send(f'No character found for {ctx.message.author} (id:{user_id})')

        except KeyError:
            await ctx.send("**Please set the authorized roles first with `addrole` before deleting an OC.**")

    @commands.hybrid_command(name='ocmodify', with_app_command=True)
    async def ocmodify(self, ctx: CustomContext):
        """ Modify OC in the database with respect to user and guild id """
        # Get guild and user roles
        guild_id = str(ctx.guild.id)
        user_roles = extract_role_ids(ctx.message.author.roles)
        user_id = ctx.author.id
        try:
            # Check if permissions have been set for the server
            roles_list = self.roles_dict[guild_id]

            # Check if user is allowed to use the database
            if any(str(role) in roles_list for role in user_roles):
                # Get OC list for specified user
                result = await self.bot.pool.fetch('SELECT * FROM characters WHERE user_id = ?', user_id)
                # List the OC(s)
                oc_list = [row['oc_name'] for row in result]  # Extract the oc_name values from the rows
                oc_list_str = "\n".join(oc_list)  # Join the oc_list elements with newlines

                def check(m):
                    return m.author == ctx.author

                # Ask what OC name to delete
                await ctx.send(
                    f"# :screwdriver: Enter the name of the character to modify from the following list:\n**{oc_list_str}**")
                try:
                    oc_name = await self.bot.wait_for('message', check=check, timeout=20)
                    oc_name = oc_name.content
                    # Check if the OC exists
                    oc = await self.bot.pool.fetch("""
                                                    SELECT * FROM characters WHERE user_id = ? AND guild_id = ? AND oc_name = ?
                                                """, ctx.message.author.id, guild_id, oc_name)
                    if not oc:
                        await ctx.send(f"**No OC found with the name {oc_name}.**")
                        return

                    # Create an instance of the OCModifier view
                    oc_modifier = OCModifier(self.bot)

                    # Wait for the user to make their selections
                    await ctx.send("**Select fields to modify:**", view=oc_modifier)
                    await oc_modifier.wait()

                    modified_field = oc_modifier.modified_field

                    # Get the modified field and update the OC in the database
                    if modified_field == 'oc_colour':
                        view = ColorPicker(bot=self.bot)
                        await ctx.send(view=view)
                        await view.wait()

                        colour = view.colour
                        await ctx.send(f'**You have picked {colour} for your OC!**')

                        print(await self.bot.pool.execute(
                            f"""UPDATE characters SET oc_colour = ? WHERE user_id = ? AND guild_id = ? AND oc_name = ?""",
                            colour, user_id, guild_id, oc_name))

                        await ctx.send(f'**OC called {oc_name} successfully modified!**')

                    elif modified_field == 'oc_picture':
                        await ctx.send("**Please send a new picture:**")
                        try:
                            new_value = await self.bot.wait_for("message", check=check, timeout=30.0)
                            new_value_content = new_value.content

                            if new_value.attachments and new_value.attachments[0].content_type in ['image/png', 'image/jpeg']:
                                oc_picture = await new_value.attachments[0].read()

                                print(await self.bot.pool.execute(
                                    f"""UPDATE characters SET oc_picture = ? WHERE user_id = ? AND guild_id = ? AND oc_name = ?""",
                                    oc_picture, user_id, guild_id, oc_name))

                                await ctx.send(f'**OC called {oc_name} successfully modified!**')

                            else:
                                # The attachment is not a PNG or JPEG file
                                await ctx.send("Please attach a **PNG** or **JPEG** file.")

                        except asyncio.TimeoutError:
                            await ctx.send("**Timed out. Please try again.**")
                            return

                    else:
                        await ctx.send("**Please input a new value:**")
                        try:
                            new_value = await self.bot.wait_for("message", check=check, timeout=30.0)
                            new_value = new_value.content
                            print(await self.bot.pool.execute(f"""UPDATE characters SET {modified_field} = ? WHERE user_id = ? AND guild_id = ? AND oc_name = ?""",
                                                        new_value, user_id, guild_id, oc_name))

                            await ctx.send(f'**OC called {oc_name} successfully modified!**')

                        except asyncio.TimeoutError:
                            await ctx.send("**Timed out. Please try again.**")
                            return

                    # set_clause = ', '.join([f'{field} = ?' for field in new_values.keys()])
                    # values = list(new_values.values()) + [ctx.message.author.id, guild_id, oc_name]
                    # await self.bot.pool.execute(f"""UPDATE characters SET {set_clause} WHERE user_id = ? AND guild_id = ? AND oc_name = ?
                    #         """, *values)

                except asyncio.TimeoutError:
                    await ctx.send("You took too long. No OC was modified.")
            else:
                await ctx.send(
                    "**If you think you should be able to modify an OC in the database, contact your local admins.**")
        except KeyError:
            await ctx.send("**Please set the authorized roles first with `addrole` before modifying an OC.**")

    @commands.hybrid_command(name='oclist', with_app_command=True)
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def oclist(self, ctx: CustomContext, artist_name):
        """ List all oc of an artist """
        rows = await self.bot.pool.fetch('SELECT oc_name FROM characters WHERE user_name = ?', artist_name)

        if rows:
            # User is in the database and has OCs
            oc_list = [row['oc_name'] for row in rows]  # Extract the oc_name values from the rows
            oc_list_str = "\n".join(oc_list)  # Join the oc_list elements with newlines
            await ctx.send(f"# :clipboard: OCs for {artist_name}:\n**{oc_list_str}**")
        else:
            # User is not in the database or does not have OCs
            await ctx.send(f"{artist_name} do not have any OCs!")

    @commands.hybrid_command(name='artistlist', with_app_command=True)
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def artistlist(self, ctx: CustomContext):
        """ List all artists of a server """
        rows = await self.bot.pool.fetch('SELECT DISTINCT user_name FROM characters WHERE guild_id = ?', ctx.guild.id)

        if rows:
            # User is in the database and has OCs
            artist_list = [row['user_name'] for row in rows]  # Extract the oc_name values from the rows
            artist_list_str = "\n".join(artist_list)  # Join the oc_list elements with newlines
            await ctx.send(f"# :clipboard: Artist with OCs:\n**{artist_list_str}**")
        else:
            # User is not in the database or does not have OCs
            await ctx.send(f"No artist has been found!")

    @commands.hybrid_command(name='ocrandom', with_app_command=True)
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def ocrandom(self, ctx: CustomContext):
        """ Send the description of a random selected OC """
        # Get sqlite row
        rows = await self.bot.pool.fetch('SELECT * FROM characters WHERE guild_id = ? ORDER BY RANDOM() LIMIT 1', ctx.guild.id)

        # Store all information
        user_id = rows[0]['user_id']
        user_name = rows[0]['user_name']
        oc_name = rows[0]['oc_name']
        oc_age = rows[0]['oc_age']
        oc_nationality = rows[0]['oc_nationality']
        oc_gender = rows[0]['oc_gender']
        oc_sexuality = rows[0]['oc_sexuality']
        oc_universe = rows[0]['oc_universe']
        oc_story = rows[0]['oc_story']
        oc_picture = rows[0]['oc_picture']
        oc_colour = int(rows[0]['oc_colour'][1:], 16)

        user = ctx.bot.get_user(user_id)
        avatar_url = user.avatar

        # Create embed
        embed, file = init_embed(user_name,
            oc_name,
            oc_age,
            oc_nationality,
            oc_gender,
            oc_sexuality,
            oc_universe,
            oc_story,
            oc_picture,
            oc_colour,
            avatar_url)

        await ctx.send(file=file, embed=embed)

    @commands.hybrid_command(name='ocinfo', with_app_command=True)
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def ocinfo(self, ctx: CustomContext, artist_name, oc_name):
        """ Gives the information sheet of an OC """
        # Get sqlite row
        rows = await self.bot.pool.fetch('SELECT * FROM characters WHERE guild_id = ? AND user_name = ? AND oc_name = ?',
                                         ctx.guild.id, artist_name, oc_name)

        # Store all information
        user_id = rows[0]['user_id']
        user_name = rows[0]['user_name']
        oc_name = rows[0]['oc_name']
        oc_age = rows[0]['oc_age']
        oc_nationality = rows[0]['oc_nationality']
        oc_gender = rows[0]['oc_gender']
        oc_sexuality = rows[0]['oc_sexuality']
        oc_universe = rows[0]['oc_universe']
        oc_story = rows[0]['oc_story']
        oc_picture = rows[0]['oc_picture']
        oc_colour = int(rows[0]['oc_colour'][1:], 16)

        user = ctx.bot.get_user(user_id)
        avatar_url = user.avatar

        # Create embed
        embed, file = init_embed(user_name, oc_name,
                           oc_age,
                           oc_nationality,
                           oc_gender,
                           oc_sexuality,
                           oc_universe,
                           oc_story,
                           oc_picture,
                           oc_colour,
                           avatar_url)

        await ctx.send(file=file, embed=embed)


async def setup(bot):
    await bot.add_cog(OCmanager(bot))

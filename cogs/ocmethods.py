import discord
import json
import os
import sqlite3 as sql

from discord.ext import commands
from utils import permissions
from utils.data import DiscordBot
from utils.default import CustomContext
from utils.misc import extract_role_ids


class OCmanager(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot
        self.db = sql.connect('database.db')
        # Check if the JSON file exists
        if not os.path.exists('roles.json'):
            open('roles.json', 'w').close()
        # If the file exists, load the data from the file
        with open('roles.json', 'r') as f:
            self.roles_dict = json.load(f)

    @commands.hybrid_command(name='addoc', with_app_command=True)
    # @commands.cooldown(rate=1, per=60, type=commands.BucketType.user)
    async def addoc(self, ctx: CustomContext):
        """ Add OC to the database with respect to user and guild id """
        # Get guild and user roles
        guild_id = str(ctx.guild.id)
        user_roles = extract_role_ids(ctx.message.author.roles)  # roles formatting needed to only keep the actual id
        try:
            # Check if permissions have been set for the server
            roles_list = self.roles_dict[guild_id]
            # Check is user is allowed to use the database
            if any(role in roles_list for role in user_roles):
                user_id = ctx.message.author.id

                def check(m):
                    return m.author == ctx.author

                await ctx.send('Enter the name of the character: ')
                name = await self.bot.wait_for('message', check=check, timeout=30)

                await ctx.send('Enter the age of the character: ')
                age = await self.bot.wait_for('message', check=check, timeout=30)

                await ctx.send('Enter the nationality of the character: ')
                nationality = await self.bot.wait_for('message', check=check, timeout=30)

                await ctx.send('Enter the gender of the character: ')
                gender = await self.bot.wait_for('message', check=check, timeout=30)

                await ctx.send('Enter the sexual orientation of the character: ')
                sexuality = await self.bot.wait_for('message', check=check, timeout=30)

                await ctx.send('Enter the universe of the character: ')
                universe = await self.bot.wait_for('message', check=check, timeout=30)

                await ctx.send('Enter the description of the character: ')
                desc = await self.bot.wait_for('message', check=check, timeout=60)

                await ctx.send('Send a picture of the character or a direct internet link: ')
                picture = await self.bot.wait_for('message', check=check, timeout=60)
                if picture.attachments is not None:
                    picture = (picture.attachments[0]).url
                else:
                    picture = picture.content

                await ctx.send("Enter the characteristic colour of the character (as hex code: https://www.color-hex.com): ")
                colour = await self.bot.wait_for('message', check=check, timeout=60)

                values = (guild_id, user_id, name.content, age.content, nationality.content, gender.content, sexuality.content, universe.content, desc.content, picture, f"0x{colour.content.replace(' #','')}")

                cursor = self.db.cursor()
                cursor.execute('INSERT INTO "guild_{}" VALUES(?,?,?,?,?,?,?,?,?,?,?)'.format(guild_id), values)
                self.db.commit()

                # Close cursor
                cursor.close()
                self.db.close()

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

                def check(m):
                    return m.author == ctx.author

                await ctx.send("Enter the name of the character to delete: ")
                oc_name = await self.bot.wait_for('message', check=check, timeout=60)
                cursor = self.db.cursor()
                cursor.execute('DELETE FROM "guild_{}" WHERE author_id = {} AND oc_name = "{}"'.format(guild_id, user_id, oc_name))
                self.db.commit()

                # Close cursor
                cursor.close()
                self.db.close()

                await ctx.send(f'Character successfully deleted for <@{user_id}>!')

        except KeyError:
            await ctx.send("**Please set the authorized roles first with `addrole` before deleting an OC.**")

    @commands.hybrid_command(name='listoc', with_app_command=True)
    async def listoc(self, ctx: CustomContext, ):
        """ List all oc of an artist, by default will list ocs at random if the user is not in the database """


async def setup(bot):
    await bot.add_cog(OCmanager(bot))

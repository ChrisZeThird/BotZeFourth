import discord
import json
import os

from discord.ext import commands
from utils.data import DiscordBot
from utils.default import CustomContext
from utils.misc import extract_role_ids
from postgreslite import PostgresLite


class OCmanager(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot
        self.db = PostgresLite('database.db')
        # Check if the JSON file exists
        if not os.path.exists('roles.json'):
            open('roles.json', 'w').close()
        # If the file exists, load the data from the file
        with open('roles.json', 'r') as f:
            self.roles_dict = json.load(f)

    @commands.hybrid_command(name='addoc', with_app_command=True)
    # @commands.cooldown(rate=1, per=60, type=commands.BucketType.user)
    async def addoc(self, ctx: CustomContext, name, age, nationality, gender, sexuality, universe, desc, picture: discord.Attachment):
        """ Add OC to the database with respect to user and guild id """
        # Get guild and user roles
        guild_id = str(ctx.guild.id)
        user_roles = extract_role_ids(ctx.message.author.roles)  # roles formatting needed to only keep the actual id
        print('check 1')
        try:
            # Check if permissions have been set for the server
            roles_list = self.roles_dict[guild_id]
            # Check is user is allowed to use the database
            print('check 2')
            if any(role in roles_list for role in user_roles):
                user_id = ctx.message.author.id

                print('check 4')
                self.db.execute('INSERT INTO "guild_{}" VALUES(?,?,?,?,?,?,?,?,?,?)'.format(guild_id), (name, age, nationality, gender, sexuality, universe, desc, picture.url))

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

                self.db.execute('DELETE FROM "guild_{}" WHERE author_id = {} AND oc_name = "{}"'.format(guild_id, user_id, oc_name))

                await ctx.send(f'Character successfully deleted for <@{user_id}>!')

        except KeyError:
            await ctx.send("**Please set the authorized roles first with `addrole` before deleting an OC.**")

    @commands.hybrid_command(name='listoc', with_app_command=True)
    async def listoc(self, ctx: CustomContext, ):
        """ List all oc of an artist, by default will list ocs at random if the user is not in the database """


async def setup(bot):
    await bot.add_cog(OCmanager(bot))

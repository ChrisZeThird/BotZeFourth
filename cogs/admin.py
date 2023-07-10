import discord
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


async def setup(bot):
    await bot.add_cog(Admin(bot))

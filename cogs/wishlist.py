import asyncio
import discord
import json
import os

from discord.ext import commands
from utils.data import DiscordBot


class WishList(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot

    @commands.hybrid_command(name='createwishlistprofile', with_app_command=True)
    # @commands.cooldown(rate=1, per=60, type=commands.BucketType.user)
    async def addtowishlist(self, ctx, item_name, item_price, item_url,):
        """ Add items to wishlist """
        # Get guild id
        guild_id = str(ctx.guild.id)


async def setup(bot):
    await bot.add_cog(WishList(bot))

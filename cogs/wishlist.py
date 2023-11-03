import asyncio
import discord
import json
import os
from table2ascii import table2ascii as t2a, PresetStyle


from discord.ext import commands
from utils.data import DiscordBot



class WishList(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot

    @commands.hybrid_command(name='addtowishlist', with_app_command=True)
    # @commands.cooldown(rate=1, per=60, type=commands.BucketType.user)
    async def addtowishlist(self, ctx, item_name, item_url):
        """ Add items to wishlist """
        # Get guild id
        guild_id = ctx.guild.id
        user_id = ctx.author.id
        user_name = ctx.message.author.name

        print(await self.bot.pool.execute("""
                            INSERT INTO wishlist (
                                  user_id, guild_id, user_name, item_name, item_url
                                )  VALUES (?, ?, ?, ?, ?) 
                            """, user_id, guild_id, user_name, item_name, item_url)
              )
        await ctx.send(f'Item successfully added to your wishlist, <@{user_id}>!')

    @commands.hybrid_command(name='checkwishlist', with_app_command=True)
    async def checkwishlist(self, ctx, user_name=None):
        """ Check a wishlist of a specific user if their name is specified, otherwise return user's own wishlist """
        if user_name is None:
            user_name = ctx.author.name

        rows = await self.bot.pool.fetch('SELECT item_name, item_url FROM wishlist WHERE user_name = ?', user_name)

        if rows:
            # Create a list of dictionaries containing the item name and url
            # items = [{'name': row['item_name'], 'url': row['item_url']} for row in rows]
            items = [[row['item_name'], row['item_url']] for row in rows]
            # TODO Find way to shorten URL because they're too large for the table
            # Create a table-looking message with the items and their urls
            output = t2a(
                header=["Item Name", "Item URL"],
                body=items,
                style=PresetStyle.thin_compact
            )

            await ctx.send(f"```\n{output}\n```")
        else:
            # User is not in the database or does not have OCs
            await ctx.send(f"{user_name} do not have any wishlist!")


async def setup(bot):
    await bot.add_cog(WishList(bot))

import time
import discord
import psutil
import os

from utils.default import CustomContext
from discord.ext import commands
from utils import default
from utils.data import DiscordBot


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot
        self.process = psutil.Process(os.getpid())

    @commands.command()
    async def ping(self, ctx: CustomContext):
        """ Pong! """
        before = time.monotonic()
        before_ws = int(round(self.bot.latency * 1000, 1))
        msg = await ctx.send("🏓 Pong")
        ping = (time.monotonic() - before) * 1000
        await msg.edit(content=f"🏓 WS: {before_ws}ms  |  REST: {int(ping)}ms")

    @commands.command(aliases=["joinme", "join", "botinvite"])
    async def invite(self, ctx: CustomContext):
        """ Invite me to your server """
        await ctx.send("\n".join([
            f"**{ctx.author.name}**, use this URL to invite me",
            f"<{discord.utils.oauth_url(self.bot.user.id)}>"
        ]))

    @commands.command(aliases=["supportserver", "feedbackserver"])
    async def botserver(self, ctx: CustomContext):
        """ Get an invitation to our support server! """
        if isinstance(ctx.channel, discord.DMChannel) or ctx.guild.id != 86484642730885120:
            return await ctx.send(f"**The template used was developed by AlexFlipnote: **\nhttps://discord.gg/DpxkY3x \n \n"
                                  f"**You can also join the server of ChrisZeThird: **\nhttps://discord.gg/TcwjZhE")


async def setup(bot):
    await bot.add_cog(Information(bot))

import time
import discord
from discord.errors import Forbidden
from discord.ext import commands
import psutil
import os

from utils.default import CustomContext
from utils import config
from utils.data import DiscordBot


class Information(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot
        self.process = psutil.Process(os.getpid())

    @commands.hybrid_command(name='help', with_app_command=True)
    async def help(self, ctx: CustomContext, *command_names):
        """ Help command, shows all modules of the bot """
        c = config.Config.from_env(".env")

        # Checks if cog parameter was given
        # Otherwise sends all modules and commands not associated with a cog
        if not command_names:
            # Starting to build embed
            embed = discord.Embed(title='Commands and modules', color=discord.Color.blue(),
                                description=f'Use `{c.discord_prefix}help <module>` or `/help <module>` to gain more information about that module!\n')

            # Iterating through cogs, gathering descriptions
            cogs_desc = ''
            for cog in self.bot.cogs:
                cogs_desc += f'`{cog}` {self.bot.cogs[cog].__doc__}\n'

            # Adding 'list' of cogs to embed
            embed.add_field(name='Modules', value=cogs_desc, inline=False)

            # Integrating trough uncategorized commands
            commands_desc = ''
            for command in self.bot.walk_commands():
                # Listing command if cog name is not None and command isn't hidden
                if not command.cog_name and not command.hidden:
                    commands_desc += f'{command.name} - {command.help}\n'

            # adding those commands to embed
            if commands_desc:
                embed.add_field(name='Not belonging to a module', value=commands_desc, inline=False)

        elif len(command_names) == 1:
            # iterating trough cogs
            for cog in self.bot.cogs:
                # check if cog is the matching one
                if cog.lower() == command_names[0].lower():

                    # making title - getting description from doc-string below class
                    embed = discord.Embed(title=f'{cog} - Commands', description=self.bot.cogs[cog].__doc__,
                                        color=discord.Color.green())

                    # getting commands from cog
                    for command in self.bot.get_cog(cog).get_commands():
                        # if cog is not hidden
                        if not command.hidden:
                            embed.add_field(name=f"`{c.discord_prefix}{command.name}`", value=command.help, inline=False)
                    # found cog - breaking loop
                    break

        # Too many cogs requested - only one at a time allowed
        elif len(command_names) > 1:
            embed = discord.Embed(title="That's too much.",
                            description="Please request only one module at once :sweat_smile:",
                            color=discord.Color.orange())

        # If the command was not found
        else:
            embed = discord.Embed(title="What's that?!",
                                description=f"I've never heard from a module called `{command_names[0]}` before.",
                                color=discord.Color.red())

        try:
            await ctx.send(embed=embed)
        except Forbidden:
            try:
                await ctx.send("Hey, seems like I can't send embeds. Make sure I have the proper permissions.")
            except Forbidden:
                await ctx.author.send(
                    f"Hey, seems like I can't send any message in {ctx.channel.name} on {ctx.guild.name}\n", embed=embed)

    @commands.hybrid_command(name='ping', with_app_command=True)
    async def ping(self, ctx: CustomContext):
        """ Pong! """
        before = time.monotonic()
        before_ws = int(round(self.bot.latency * 1000, 1))
        msg = await ctx.send("🏓 Pong")
        ping = (time.monotonic() - before) * 1000
        await msg.edit(content=f"🏓 WS: {before_ws}ms  |  REST: {int(ping)}ms")

    @commands.hybrid_command
    async def invite(self, ctx: CustomContext):
        """ Invite me to your server """
        await ctx.send("\n".join([
            f"**{ctx.author.name}**, use this URL to invite me",
            f"<{discord.utils.oauth_url(self.bot.user.id)}>"
        ]))

    @commands.hybrid_command(name='botserver', with_app_command=True)
    async def botserver(self, ctx: CustomContext):
        """ Get an invitation to our support server! """
        if isinstance(ctx.channel, discord.DMChannel) or ctx.guild.id != 86484642730885120:
            return await ctx.send(f"**The template used was developed by AlexFlipnote: **\nhttps://discord.gg/DpxkY3x \n \n"
                                  f"**You can also join the server of ChrisZeThird: **\nhttps://discord.gg/TcwjZhE")


async def setup(bot):
    await bot.add_cog(Information(bot))

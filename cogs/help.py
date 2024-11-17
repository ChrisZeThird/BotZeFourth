import discord
from discord.ext import commands

from utils.misc import add_spaces_to_capital_letters


class Help(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name='help', description='Shows list of commands', with_app_command=True)
    async def help(self, ctx, *, arg=None):
        if arg is None:
            # Display regular help command
            embed = discord.Embed(title="BotZeFourth Commands List", description="Categories and corresponding commands available", color=0xff0000)
            for c in self.bot.cogs:
                cog = self.bot.get_cog(c)
                if len([cog.walk_commands()]) and cog.qualified_name not in ['Artwork', 'Events']:
                    print(cog.qualified_name)
                    embed.add_field(name=add_spaces_to_capital_letters(cog.qualified_name), value=', '.join(f"`{i.name}`" for i in cog.walk_commands()))
            await ctx.send(embed=embed)
        else:
            # Check if the argument is a category or a command
            command = self.bot.get_command(arg)
            if command:
                # Display information about the specified command wit args
                embed = discord.Embed(
                    title=f"`{command.name}`",
                    description=command.help or "No description provided.",
                    color=0xff0000
                )
                embed.add_field(name="Usage", value=f"/{command.name} `{command.signature}`", inline=False)
                await ctx.send(embed=embed)
            else:
                # Check if the argument is a category
                cog = self.bot.get_cog(arg.replace(" ", ""))
                if cog and cog.qualified_name not in ['Artwork', 'Events']:
                    # Display commands within the specified category
                    embed = discord.Embed(title=f"{arg} Commands",
                                          description=', '.join(f"`{i.name}`" for i in cog.walk_commands()),
                                          color=0xff0000)
                    await ctx.send(embed=embed)
                else:
                    await ctx.send("Invalid command or category.")


async def setup(bot):
    await bot.add_cog(Help(bot))

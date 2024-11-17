import discord
import json
import psutil
import os

from datetime import datetime
from utils.default import CustomContext
from discord.ext import commands
from discord.ext.commands import errors
from postgreslite import PostgresLite
from utils import default
from utils.data import DiscordBot


class Events(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot
        self.process = psutil.Process(os.getpid())

    @commands.Cog.listener()
    async def on_command_error(self, ctx: CustomContext, err: Exception):
        # Define the target server and channel IDs
        TARGET_GUILD_ID = 1307424009163374653  # Replace with your Discord server (guild) ID
        TARGET_CHANNEL_ID = 1307424995965931602  # Replace with your target channel ID

        if isinstance(err, errors.MissingRequiredArgument) or isinstance(err, errors.BadArgument):
            helper = str(ctx.invoked_subcommand) if ctx.invoked_subcommand else str(ctx.command)
            # Fetch the target channel
            target_guild = self.bot.get_guild(TARGET_GUILD_ID)  # Replace `self.bot` with your bot's instance if needed
            if target_guild:
                target_channel = target_guild.get_channel(TARGET_CHANNEL_ID)
                if not target_channel:
                    target_channel = await target_guild.fetch_channel(TARGET_CHANNEL_ID)

                if target_channel:
                    await target_channel.send(f"Error details: {helper}")

            # Send a generic message to the current channel
            await ctx.send("There was an error processing the command ;-;")

        elif isinstance(err, errors.CommandInvokeError) or isinstance(err, errors.HybridCommandError):
            error = default.traceback_maker(err.original)
            print(default.traceback_maker(err))
            if "2000 or fewer" in str(err) and len(ctx.message.clean_content) > 1900:
                return await ctx.send("\n".join([
                    "You attempted to make the command display more than 2,000 characters...",
                    "Both error and command will be ignored."
                ]))

            await ctx.send(f"There was an error processing the command ;-;")

        elif isinstance(err, errors.CheckFailure):
            pass

        elif isinstance(err, errors.MaxConcurrencyReached):
            await ctx.send("You've reached max capacity of command usage at once, please finish the previous one...")

        elif isinstance(err, errors.CommandOnCooldown):
            cd: int = int(err.retry_after)
            await ctx.send(f"This command is on cooldown... try again in {cd//86400}d {(cd//3600)%24}h {(cd//60)%60}m {cd % 60}.")

        elif isinstance(err, errors.CommandNotFound):
            pass

    @commands.Cog.listener()
    async def on_guild_join(self, guild: discord.Guild):
        to_send = next((
            chan for chan in guild.text_channels
            if chan.permissions_for(guild.me).send_messages
        ), None)

        if to_send:
            await to_send.send(self.bot.config.discord_join_message)

    @commands.Cog.listener()
    async def on_command(self, ctx: CustomContext):
        location_name = ctx.guild.name if ctx.guild else "Private message"
        command_name = ctx.command.name if ctx.command else "Unknown command"
        print(f"{location_name} > {ctx.author} > {command_name}")

    @commands.Cog.listener()
    async def on_ready(self):
        """ The function that activates when boot was completed """
        if not hasattr(self.bot, "uptime"):
            self.bot.uptime = datetime.now()

        db = PostgresLite('database.db')
        self.bot.pool = await db.connect_async()

        await self.bot.tree.sync()

        # Check if user desires to have something other than online
        status = self.bot.config.discord_status_type.lower()
        status_type = {"online": discord.Status.online, "dnd": discord.Status.dnd}

        # Check if user desires to have a different type of activity
        activity = self.bot.config.discord_activity_type.lower()
        activity_type = {"listening": 2, "watching": 3, "competing": 5}

        await self.bot.change_presence(
            activity=discord.Game(
                type=activity_type.get(activity, 0),
                name=self.bot.config.discord_activity_name
            ),
            status=status_type.get(status, discord.Status.online)
        )

        # Indicate that the bot has successfully booted up
        print(f"Ready: {self.bot.user} | Servers: {len(self.bot.guilds)}")
        # print('Server ID: 'self.bot.guilds)
        # guild_dic = {}

        # for guild in self.bot.guilds:
        #     text_channel_list = []
        #     for channel in guild.channels:
        #         if str(channel.type) == 'text':
        #             text_channel_list.append((channel.id, channel.name))
        #     guild_dic[str(guild.name)] = text_channel_list
        # print(guild_dic["J-Productions's server"])


async def setup(bot):
    await bot.add_cog(Events(bot))

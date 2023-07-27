import discord
from discord import Intents
from utils import config, data

config = config.Config.from_env(".env")
print("Logging in...")

intents = Intents.all()
bot = data.DiscordBot(
    config=config, command_prefix=config.discord_prefix,
    prefix=config.discord_prefix, command_attrs=dict(hidden=True),
    help_command=None,
    allowed_mentions=discord.AllowedMentions(
        everyone=False, roles=False, users=True
    ),
    intents=intents
)

try:
    bot.run(config.discord_token)
except Exception as e:
    print(f"Error when logging in: {e}")

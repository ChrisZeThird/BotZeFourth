import discord
import humanize

from utils import permissions, default
from utils.config import Config
from utils.misc import ordinal_suffix
from discord.ext import commands

from utils.default import CustomContext


class ConfirmSuggestion(discord.ui.View):
    def __init__(self, bot, user_id, guild_id, suggestion) -> None:
        super().__init__(timeout=60)
        self.bot = bot
        self.user_id = user_id
        self.guild_id = guild_id
        self.suggestion = suggestion

    @discord.ui.button(label="Confirm", style=discord.ButtonStyle.green, custom_id="confirm")
    async def confirm(self, interaction: discord.Interaction, button: discord.ui.button):
        print(await self.bot.pool.execute("""
                                    INSERT INTO suggestion (
                                          user_id, guild_id, suggestion)  VALUES (?, ?, ?) 
                                    """, self.user_id, self.guild_id, self.suggestion)
              )
        await interaction.response.send_message("Your suggestion has been sent! Thank you for your contribution")
        self.stop()

    @discord.ui.button(label="Cancel", style=discord.ButtonStyle.red)
    async def cancel_button(self, interaction: discord.Interaction):
        await interaction.response.send_message("Suggestion cancelled.")
        self.stop()


class Suggestion(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.hybrid_command(name="suggest", with_app_command=True)
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def suggest(self, ctx: CustomContext, suggestion: str):
        """ Make a suggestion to the developer """
        user_id = ctx.message.author.id
        guild_id = ctx.message.guild.id

        view = ConfirmSuggestion(self.bot, user_id, guild_id, suggestion)
        # Send a message with the view
        await ctx.send("Please confirm your suggestion:", view=view)

    @commands.hybrid_command(name="suggestionvote", with_app_command=True)
    @commands.cooldown(1, 86400, commands.BucketType.user)
    async def suggestionvote(self, ctx: CustomContext, suggestion_id: int):
        """ Vote for a suggestion """
        # Increment the votes for the suggestion
        print(await self.bot.pool.execute("UPDATE suggestion SET votes = votes + 1 WHERE id = ?",
                   suggestion_id)
              )

        # Send a message with the formatted time remaining
        await ctx.send(f"Your vote has been recorded!")

    @commands.hybrid_command(name="suggestionranking")
    async def suggestionranking(self, ctx: CustomContext):
        """ Check ranking of suggestion """
        # Retrieve the top suggestions
        top_suggestions = await self.bot.pool.fetch(
            "SELECT id, suggestion, votes FROM suggestion ORDER BY votes DESC")

        # Format the suggestions as a string
        suggestions_str = "\n".join([f"** {ordinal_suffix(i+1)}**: {s['suggestion']} *(ID: {s['id']} | Votes: {s['votes']})*" for s, i in zip(top_suggestions, range(len(top_suggestions)))])

        # Send the top suggestions
        # await ctx.send(f"# :bookmark_tabs:  Top suggestions:\n{suggestions_str}")
        embed = discord.Embed(title="List of suggestions", description=f"{suggestions_str}",
                              color=0xffffff)
        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Suggestion(bot))

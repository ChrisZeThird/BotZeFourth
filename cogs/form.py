import discord
from discord import app_commands
from discord.ext import commands
from discord import ui


class FormModal(ui.Modal, title='User Information Form'):
    name = ui.TextInput(label='Name')
    age = ui.TextInput(label='Age')
    favorite_color = ui.TextInput(label='Favorite Color')
    bio = ui.TextInput(label='Bio', style=discord.TextStyle.paragraph)

    async def on_submit(self, interaction: discord.Interaction):
        # Print user input to console
        print(f"Name: {self.name.value}")
        print(f"Age: {self.age.value}")
        print(f"Favorite Color: {self.favorite_color.value}")
        print(f"Bio: {self.bio.value}")

        await interaction.response.send_message(f'Thanks for your response, {self.name}!', ephemeral=True)


class FormCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    async def form(self, ctx: commands.Context):
        """Send a form to the user"""
        if isinstance(ctx, discord.Interaction):
            # This is a slash command invocation
            await ctx.response.send_modal(FormModal())
        else:
            # This is a regular text command invocation
            modal = FormModal()
            await ctx.send("Please use the slash command version of this command to access the form.")


async def setup(bot):
    await bot.add_cog(FormCog(bot))

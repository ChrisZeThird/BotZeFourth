import discord
from discord import app_commands
from discord.ext import commands
from discord import ui

from typing import List


class FormModal(ui.Modal, title='User Information Form'):
    def __init__(self, title: str, fields: List[str], template_name: str):
        super().__init__(title=title)
        self.template_name = template_name
        self.user_inputs = {}

        # Dynamically add fields to the modal
        for field in fields:
            self.add_item(
                ui.TextInput(
                    label=field,
                    placeholder=f"Enter {field}"
                )
            )

    async def on_submit(self, interaction: discord.Interaction):
        # Collect and store user input for each field
        for item in self.children:
            self.user_inputs[item.label] = item.value

        await interaction.response.send_message(
            f"Form for template `{self.template_name}` submitted! Data: {self.user_inputs}",
            ephemeral=True
        )

        # Return the collected data (could be passed to `ocadd` for further processing)
        return self.user_inputs

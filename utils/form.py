import discord
from discord import ui, Interaction, TextStyle

from typing import List


class MyModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.TextInput(label="Short Input"))
        self.add_item(discord.ui.TextInput(label="Long Input", style=TextStyle.long))

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message('Cool thanks!', ephemeral=True)


class DynamicFormModal(ui.Modal, title='User Information Form'):
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

    async def on_submit(self, interaction: Interaction):
        # Collect and store user input for each field
        for item in self.children:
            self.user_inputs[item.label] = item.value

        await interaction.response.send_message(
            f"Form for template `{self.template_name}` submitted! Data: {self.user_inputs}",
            ephemeral=True
        )

        # Return the collected data (could be passed to `ocadd` for further processing)
        return self.user_inputs


class CompactAbilityModal(ui.Modal, title="Let's start with Ability **Scores and Modifiers**"):
    def __init__(self, title: str):
        super().__init__(title=title)
        self.ability_data = {}
        self.ability_scores = ui.TextInput(
            label="Ability Scores",
            placeholder="Enter scores in order: STR, DEX, CON, INT, WIS, CHA",
            style=TextStyle.short
        )
        self.ability_modifiers = ui.TextInput(
            label="Ability Modifiers",
            placeholder="Enter modifiers in order: STR_MOD, DEX_MOD, CON_MOD, INT_MOD, WIS_MOD, CHA_MOD",
            style=TextStyle.short
        )

    async def on_submit(self, interaction: Interaction):
        # Parse the ability scores
        try:
            scores = list(map(int, self.ability_scores.value.split(',')))
            modifiers = list(map(int, self.ability_modifiers.value.split(',')))

            # Validate the number of entries
            if len(scores) != 6 or len(modifiers) != 6:
                raise ValueError("Invalid number of scores or modifiers provided.")
        except ValueError as e:
            await interaction.response.send_message(
                f"Error: {e}\nPlease enter exactly 6 values for both scores and modifiers.",
                ephemeral=True
            )
            return

        # Process the valid data
        self.ability_data = {
            "strength": scores[0], "dexterity": scores[1], "constitution": scores[2],
            "intelligence": scores[3], "wisdom": scores[4], "charisma": scores[5],
            "str_mod": modifiers[0], "dex_mod": modifiers[1], "con_mod": modifiers[2],
            "int_mod": modifiers[3], "wis_mod": modifiers[4], "cha_mod": modifiers[5],
        }

        # Acknowledge the submission and display the parsed data
        await interaction.response.send_message(
            f"Thanks for submitting! Here's what we got:\n{self.ability_data}",
            ephemeral=True
        )

        return self.ability_data

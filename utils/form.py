import discord
from discord import ui, Interaction, TextStyle

from typing import List


class OCModal(discord.ui.Modal):
    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)

        self.add_item(discord.ui.TextInput(label="Short Input"))
        self.add_item(discord.ui.TextInput(label="Long Input", style=TextStyle.long))

    async def on_submit(self, interaction: discord.Interaction):
        await interaction.response.send_message('Cool thanks!', ephemeral=True)


class DynamicFormModal(ui.Modal, title='Placeholder'):
    def __init__(self, title: str, fields: List[str], template_name: str, placeholders=None, required=True):
        super().__init__(title=title)
        self.template_name = template_name
        self.user_inputs = {}
        self.placeholders = placeholders
        self.required = required

        # Dynamically add fields to the modal
        if placeholders is None:
            for field in fields:
                self.add_item(
                    ui.TextInput(
                        label=field,
                        placeholder=f"Enter {field}",
                        required=required
                    )
                )
        else:
            for field, placeholder in zip(fields, placeholders):
                self.add_item(
                    ui.TextInput(
                        label=field,
                        placeholder=placeholder,
                        required=required
                    )
                )

    async def on_submit(self, interaction: Interaction):
        # Collect and store user input for each field
        for item in self.children:
            # Use item.value if it's not empty; otherwise, use item.placeholder
            self.user_inputs[item.label] = item.value if item.value else item.placeholder

        formatted_output = f"Form for template `{self.template_name}` submitted! Data: : " + "; ".join(
            [f"`{key}`: {value}" for key, value in self.user_inputs.items()]
        )
        await interaction.response.send_message(
            formatted_output,
            ephemeral=True
        )
        self.stop()  # Stop the modal to allow the next modal to be sent


class CompactAbilityModal(ui.Modal, title="Ability Scores and Modifiers"):
    def __init__(self, title: str):
        super().__init__(title=title)
        self.user_inputs = {}
        self.add_item(ui.TextInput(
            label="Ability Scores",
            placeholder="Enter scores in order: STR, DEX, CON, INT, WIS, CHA",
            style=TextStyle.long
        ))
        self.add_item(ui.TextInput(
            label="Ability Modifiers",
            placeholder="Enter modifiers in order: STR_MOD, DEX_MOD, CON_MOD, INT_MOD, WIS_MOD, CHA_MOD",
            style=TextStyle.long
        ))

    async def on_submit(self, interaction: Interaction):
        # Collect and store user input for each field
        for item in self.children:
            self.user_inputs[item.label] = item.value

        # Process the input for Ability Scores and Modifiers
        try:
            ability_scores = self.user_inputs.get("Ability Scores")
            ability_modifiers = self.user_inputs.get("Ability Modifiers")

            scores = list(map(int, ability_scores.split(',')))
            modifiers = list(map(int, ability_modifiers.split(',')))

            # Process the valid data
            self.user_inputs = {
                "strength": scores[0], "dexterity": scores[1], "constitution": scores[2],
                "intelligence": scores[3], "wisdom": scores[4], "charisma": scores[5],
                "str_mod": modifiers[0], "dex_mod": modifiers[1], "con_mod": modifiers[2],
                "int_mod": modifiers[3], "wis_mod": modifiers[4], "cha_mod": modifiers[5],
            }

            # Create a formatted string
            formatted_data = (
                f"**Attributes:**\n"
                f"- Strength: {self.user_inputs['strength']} (Modifier: {self.user_inputs['str_mod']})\n"
                f"- Dexterity: {self.user_inputs['dexterity']} (Modifier: {self.user_inputs['dex_mod']})\n"
                f"- Constitution: {self.user_inputs['constitution']} (Modifier: {self.user_inputs['con_mod']})\n"
                f"- Intelligence: {self.user_inputs['intelligence']} (Modifier: {self.user_inputs['int_mod']})\n"
                f"- Wisdom: {self.user_inputs['wisdom']} (Modifier: {self.user_inputs['wis_mod']})\n"
                f"- Charisma: {self.user_inputs['charisma']} (Modifier: {self.user_inputs['cha_mod']})"
            )

            await interaction.response.send_message(f'Characters information successfully saved!\n{formatted_data}',
                                                    ephemeral=True)
            self.stop()  # Stop the modal to allow the next modal to be sent

        except ValueError as e:
            await interaction.response.send_message(
                f"Error: `{e}`\n**Please enter exactly 6 values for both scores and modifiers as shown in the placeholder.**",
                ephemeral=True
            )
            raise Exception("Invalid input in ability scores or modifiers.")  # Raise exception to stop command


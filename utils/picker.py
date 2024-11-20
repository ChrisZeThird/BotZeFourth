import asyncio
import discord

from utils.form import DynamicFormModal, CompactAbilityModal, OCModal

colors = {
        "red": "#FF0000",
        "blue": "#0000FF",
        "green": "#00FF00",
        "yellow": "#FFFF00",
        "orange": "#FFA500",
        "brown": "#A52A2A",
        "white": "#FFFFFF",
        "black": "#000000",
        "purple": "#800080"
    }


class ColorPicker(discord.ui.View):

    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.colour = "#000000"

    @discord.ui.select(
        placeholder="Select a colour for your oc.",
        options=[
            discord.SelectOption(label="White", value=colors["white"], emoji='⚪'),
            discord.SelectOption(label="Black", value=colors["black"], emoji='⚫'),
            discord.SelectOption(label="Purple", value=colors["purple"], emoji='🟣'),
            discord.SelectOption(label="Blue", value=colors["blue"], emoji='🔵'),
            discord.SelectOption(label="Green", value=colors["green"], emoji='🟢'),
            discord.SelectOption(label="Yellow", value=colors["yellow"], emoji='🟡'),
            discord.SelectOption(label="Orange", value=colors["orange"], emoji='🟠'),
            discord.SelectOption(label="Red", value=colors["red"], emoji='🔴'),
            discord.SelectOption(label="Brown", value=colors["brown"], emoji='🟤'),
            discord.SelectOption(label="Custom", value="custom", emoji='🎨')
        ]
    )
    async def select_colour(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        if select_item.values[0] == "custom":
            # Prompt the user to input a hex code
            await interaction.response.send_message("Please input a hex code for your custom color.")
            try:
                # Wait for the user's response
                response = await self.bot.wait_for("message", check=lambda m: m.author == interaction.user,
                                                   timeout=30.0)
                # Set the color to the user's input
                self.colour = response.content
                print(response)
            except asyncio.TimeoutError:
                # Handle timeout
                await interaction.response.send_message("Timed out. Please try again.")
                return
        else:
            # Set the color to the selected option
            self.colour = select_item.values[0]
        self.children[0].disabled = True
        await interaction.message.edit(view=self)
        await interaction.response.defer()
        self.stop()


class MySelectMenu(discord.ui.Select):
    def __init__(self, labels, values, bot):
        self.bot = bot
        self.labels = labels
        options = []
        for label, value in zip(labels, values):
            options.append(discord.SelectOption(label=label, value=value))
        super().__init__(placeholder='Select an option...', min_values=1, max_values=1, options=options)

    # From value creates Modal fields
    async def select_template(self, value):
        """
        Retrieve columns for the selected value to parse as arguments in the modal class
        :param value: Table name, str
        :return: list to create fields of modal
        """
        query = f"PRAGMA table_info({value})"
        columns = await self.bot.pool.fetch(query)
        column_names = [row['name'] for row in columns]

        # Skip DB-related fields and chunk columns for modal fields
        user_fields = column_names[:2]  # Assuming first 2 are DB info
        character_fields = column_names[2:]
        exclude_fields = ["picture_url", "color", "template_id"]

        if value == 'DnDCharacters':
            # Custom handling for DnDCharacters template
            ability_scores = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
            ability_modifiers = ["str_mod", "dex_mod", "con_mod", "int_mod", "wis_mod", "cha_mod"]

            # Split fields into chunks of 5 for modals
            user_fields = [field for field in character_fields if
                           field not in ability_scores + ability_modifiers + exclude_fields]
            field_chunks = [user_fields[i:i + 5] for i in
                            range(0, len(user_fields), 5)]
        else:
            user_fields = [field for field in character_fields if field not in exclude_fields]
            field_chunks = [user_fields[i:i + 5] for i in range(0, len(user_fields), 5)]

        return field_chunks

    async def callback(self, interaction: discord.Interaction):
        self.view.value = self.values[0]  # Save the selected value for later use
        field_chunks = await self.select_template(self.view.value)

        # Send the first modal
        await self.loop_through_modals(interaction, field_chunks, self.view.value)

    async def loop_through_modals(self, interaction: discord.Interaction, field_chunks, template_name):
        # Create Modal object
        modal = DynamicFormModal(title='Character Creation', fields=field_chunks[0], template_name=template_name)
        await interaction.response.send_modal(modal)
        await modal.wait()

        chunk_number = len(field_chunks)

        index = 1
        for index in range(1, chunk_number):
            # Create and send the modal
            followup_modal = DynamicFormModal(
                title=f'Character Creation (Step {index}/{chunk_number})',
                fields=field_chunks[index],
                template_name=template_name
            )

            # Send the confirmation button
            view = NextModalButton(followup_modal)
            await interaction.followup.send(
                content=f"Step {index} out of {chunk_number}. Please click 'Next' to continue.",
                view=view,
                ephemeral=True  # Optionally make it ephemeral
            )

            await view.wait()  # Wait for the confirmation button to be clicked

        # # Use the new interaction from the button to send the next modal
        # index += 1  # Move to the next chunk

        # Send extra ability modal if DnDCharacters is selected
        if template_name == 'DnDCharacters':
            ability_modal = CompactAbilityModal(title=f'Character Creation (Extra step)')
            # Send the confirmation button
            view = NextModalButton(ability_modal)
            await interaction.followup.send(
                content=f"Extra step. Please click 'Next' to continue.",
                view=view,
                ephemeral=True  # Optionally make it ephemeral
            )

            await view.wait()  # Wait for the confirmation button to be clicked



class MyView(discord.ui.View):
    def __init__(self, labels, values, bot):
        super().__init__()
        self.value = None
        self.add_item(MySelectMenu(labels, values, bot=bot))


class NextModalButton(discord.ui.View):
    def __init__(self, modal):
        super().__init__()
        self.next_interaction = None
        self.modal = modal

    @discord.ui.button(label='Next', style=discord.ButtonStyle.primary)
    async def next_button(self, button_interaction: discord.Interaction, button: discord.ui.Button):
        await button_interaction.response.send_modal(self.modal)
        self.stop()  # Stop the view to continue

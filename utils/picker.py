import asyncio
import discord

from utils.form import MyModal

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
    def __init__(self, labels, values):
        self.labels = labels
        options = []
        for label, value in zip(labels, values):
            options.append(discord.SelectOption(label=label, value=value))
        super().__init__(placeholder='Select an option...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        self.view.value = self.values[0]  # Save the selected value for later use
        # await interaction.response.send_message(f"Selection: {self.view.value}", ephemeral=True)
        await interaction.response.send_modal(MyModal(title='Test'))
        self.view.stop()


class MyView(discord.ui.View):
    def __init__(self, labels, values):
        super().__init__()
        self.value = None
        self.add_item(MySelectMenu(labels, values))


class ConfirmButton(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.confirmed = False

    @discord.ui.button(label="Next Modal", style=discord.ButtonStyle.green)
    async def next_modal(self, button: discord.ui.Button, interaction: discord.Interaction):
        self.confirmed = True
        await interaction.response.send_message("Selection confirmed, proceeding...", ephemeral=True)
        self.stop()

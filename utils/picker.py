import asyncio
import discord

# Color picker
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


# General definition of select menu
class MySelectMenu(discord.ui.Select):
    def __init__(self, labels, values):
        self.labels = labels
        options = []
        for label, value in zip(labels, values):
            options.append(discord.SelectOption(label=label, value=value))
        super().__init__(placeholder='Select an option...', min_values=1, max_values=1, options=options)

    async def callback(self, interaction: discord.Interaction):
        self.view.value = self.values[0]  # Save the selected value for later use
        self.view.stop()


class MyView(discord.ui.View):
    def __init__(self, labels, values):
        super().__init__()
        self.value = None
        self.add_item(MySelectMenu(labels, values))


# Button for character statistics definition
class StatButtons(discord.ui.Button):
    def __init__(self, label):
        super().__init__(style=discord.ButtonStyle.secondary, label=label)
        self.label = label

    # This function is called whenever this particular button is pressed
    async def callback(self, interaction: discord.Interaction):
        assert self.view is not None
        view: OCStat = self.view
        view.selected_label = self.label  # Store the selected label in the OCStat view
        view.stop()
        # await interaction.response.send_message(self.label)


# This is our actual statistics selection View
class OCStat(discord.ui.View):
    def __init__(self):
        super().__init__()
        self.selected_label = None
        for i in range(11):
            self.add_item(StatButtons(label=str(i)))


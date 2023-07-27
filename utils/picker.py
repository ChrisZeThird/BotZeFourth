import asyncio
import discord

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


class OCModifier(discord.ui.View):
    def __init__(self, bot, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = bot
        self.modified_field = ""
        self.colour = None

    @discord.ui.select(
        placeholder="Select a field to modify for your OC.",
        options=[
            discord.SelectOption(label="OC Name", value="oc_name"),
            discord.SelectOption(label="OC Age", value="oc_age"),
            discord.SelectOption(label="OC Nationality", value="oc_nationality"),
            discord.SelectOption(label="OC Gender", value="oc_gender"),
            discord.SelectOption(label="OC Sexuality", value="oc_sexuality"),
            discord.SelectOption(label="OC Universe", value="oc_universe"),
            discord.SelectOption(label="OC Story", value="oc_story"),
            discord.SelectOption(label="OC Picture", value="oc_picture"),
            discord.SelectOption(label="OC Colour", value="oc_colour")
        ]
    )
    async def select_field(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        self.modified_field = select_item.values[0]
        self.children[0].disabled = True
        await interaction.message.edit(view=self)
        await interaction.response.defer()
        self.stop()

import discord

# colour_options = [
#     {'label': 'White', 'value': 'White', 'emoji': '⚪'},
#     {'label': 'Black', 'value': 'Black', 'emoji': '⚫'},
#     {'label': 'Blue', 'value': 'Blue', 'emoji': '🔵'},
#     {'label': 'Brown', 'value': 'Brown', 'emoji': '🟤'},
#     {'label': 'Green', 'value': 'Green', 'emoji': '🟢'},
#     {'label': 'Orange', 'value': 'Orange', 'emoji': '🟠'},
#     {'label': 'Purple', 'value': 'Purple', 'emoji': '🟣'},
#     {'label': 'Red', 'value': 'Red', 'emoji': '🔴'},
#     {'label': 'Yellow', 'value': 'Yellow', 'emoji': '🟡'}
# ]

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
    colour = None

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
            discord.SelectOption(label="Brown", value=colors["brown"], emoji='🟤')
        ]
    )
    async def select_colour(self, interaction: discord.Interaction, select_item: discord.ui.Select):
        self.colour = select_item.values
        self.children[0].disabled = True
        await interaction.message.edit(view=self)
        await interaction.response.defer()
        self.stop()

# await ctx.send("Enter the characteristic colour of the character (as hex code: https://www.color-hex.com): ")
# colour = await self.bot.wait_for('message', check=check, timeout=60)

# select = Select(max_values=1, placeholder='Select a colour!', options=options)

# async def my_callback(interaction: discord.Interaction):
#     await interaction.response.send_message(f'You chose: {select.values[0]}')
#     global colour
#     colour = select.values[0]
#
# select.callback = my_callback
# view = View()
# view.add_item(select)
# await ctx.send('Select a colour!', view=view)

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


class ColorPicker(discord.ui.View):
    colour = None

    @discord.ui.select(
        placeholder="Select a colour for your oc.",
        options=[
            discord.SelectOption(label="White", value="white", emoji='⚪'),
            discord.SelectOption(label="Black", value="black", emoji='⚫'),
            discord.SelectOption(label="Purple", value="purple", emoji='🟣'),
            discord.SelectOption(label="Blue", value="blue", emoji='🔵'),
            discord.SelectOption(label="Green", value="green", emoji='🟢'),
            discord.SelectOption(label="Yellow", value="yellow", emoji='🟡'),
            discord.SelectOption(label="Orange", value="orange", emoji='🟠'),
            discord.SelectOption(label="Red", value="red", emoji='🔴'),
            discord.SelectOption(label="Brown", value="brown", emoji='🟤')
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

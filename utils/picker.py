options = [
            {'label': 'White', 'value': 'White', 'emoji': '⚪'},
            {'label': 'Black', 'value': 'Black', 'emoji': '⚫'},
            {'label': 'Blue', 'value': 'Blue', 'emoji': '🔵'},
            {'label': 'Brown', 'value': 'Brown', 'emoji': '🟤'},
            {'label': 'Green', 'value': 'Green', 'emoji': '🟢'},
            {'label': 'Orange', 'value': 'Orange', 'emoji': '🟠'},
            {'label': 'Purple', 'value': 'Purple', 'emoji': '🟣'},
            {'label': 'Red', 'value': 'Red', 'emoji': '🔴'},
            {'label': 'Yellow', 'value': 'Yellow', 'emoji': '🟡'}
        ]


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
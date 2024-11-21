import asyncio
import discord
import json
import os
import random
from io import BytesIO

from discord.ext import commands
from utils.data import DiscordBot
from utils.default import CustomContext
from utils.embed import PaginatedOCView, create_embed
from utils.misc import extract_role_ids, open_json, concatenate_dict_values, get_key_by_value
from utils.picker import ColorPicker, MyView


async def fetch_oc_information(bot, table_name, character_name, user_id):
    """
    Fetch OC information from a specified table.

    :param bot: asyncpg connection pool.
    :param table_name: Name of the table to query.
    :param character_name: Name of the character to fetch.
    :param user_id: User ID associated with the OC.

    Returns:
        dict: Dictionary of OC information with column names as keys.
    """
    query = f"SELECT * FROM {table_name} WHERE character_name = $1 AND user_id = $2"
    result = await bot.pool.fetchrow(query, character_name, user_id)

    if result:
        return dict(result)
    else:
        return {}


class OcManager(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot
        # Check if the JSON file exists
        if not os.path.exists('roles.json'):
            open('roles.json', 'w').close()
        # If the file exists, load the data from the file
        with open('roles.json', 'r') as f:
            self.roles_dict = json.load(f)
        self.exclude_fields = ["picture_url", "color", "template_id"]

    async def selectTemplate(self):
        """
        Simple function to get the list of template name
        :return:
        """
        # Select the Template
        rows = await self.bot.pool.fetch('SELECT * FROM Templates')
        template_names = [row['template_name'] for row in rows]
        return template_names

    async def find_matching_id(self, guild_id):
        """
        Find all artists user_id for a given guild_id
        :param guild_id:
        :return:
        """
        # Step 1: Get all the template names from the Templates table
        template_names = await self.selectTemplate()

        # Step 2: Find user_ids from all tables where guild_id matches the current guild
        matching_user_ids = set()
        for table_name in template_names:
            query = f'SELECT DISTINCT user_id FROM {table_name} WHERE guild_id = $1'
            result = await self.bot.pool.fetch(query, guild_id)
            matching_user_ids.update(row['user_id'] for row in result)

        return list(matching_user_ids)

    @commands.hybrid_command(name='ocadd', with_app_command=True)
    async def ocadd(self, ctx, picture: discord.Attachment):
        """
        Add OC to the database with respect to user and guild id
        """
        # Get guild and user role
        guild_id = str(ctx.guild.id)
        user_roles = extract_role_ids(ctx.message.author.roles)
        user_id = ctx.message.author.id

        self.roles_dict = open_json()

        try:
            # Check if permissions have been set for the server
            roles_list = self.roles_dict[guild_id]
            # Check is user is allowed to use the database
            if any(str(role) in roles_list for role in user_roles):
                if picture.content_type in ['image/png', 'image/jpeg']:
                    def check(m):
                        return m.author == ctx.author

                    # Create instance of the ColorPicker DropdownMenu view
                    color_view = ColorPicker(bot=self.bot)
                    await ctx.send(view=color_view)
                    await color_view.wait()
                    color = color_view.colour
                    await ctx.send(f'You have picked {color} for your OC!')

                    # Select the Template
                    template_names = self.selectTemplate()
                    # Create an instance of the DropdownMenu view for the oc names
                    template_selector = MyView(labels=template_names, values=template_names, bot=self.bot)
                    await ctx.send(content='**Select the template to use**', view=template_selector)
                    await template_selector.wait()  # continues after stop() or timeout

                    template = template_selector.value
                    # Get data to store
                    data = template_selector.data_to_store
                    # Prepare the picture to be stored in the database
                    oc_picture = await picture.read()
                    # Consolidate the list of dictionaries into a single dictionary
                    consolidated_data = {}
                    for entry in data:
                        consolidated_data.update(entry)
                    consolidated_data.update({'user_id': user_id,
                                              'guild_id': guild_id,
                                              'picture_url': oc_picture,
                                              'color': color})

                    # Fetch the template's column names and values to store
                    columns = list(consolidated_data.keys())
                    values = list(consolidated_data.values())
                    # Create placeholders for SQL query (e.g., '?, ?, ?, ...')
                    placeholders = ', '.join(['?'] * len(columns))
                    # Construct the query string dynamically
                    query = f"INSERT INTO {template} ({', '.join(columns)}) VALUES ({placeholders})"
                    # Execute the query
                    print(await self.bot.pool.execute(query, *values))
                    await ctx.send(f'Character successfully added for <@{user_id}>!')

                    # Update JSON with user_id and guild_id
                    json_file = 'user_guilds.json'
                    if os.path.exists(json_file):
                        with open(json_file, 'r') as f:
                            user_data = json.load(f)
                    else:
                        user_data = {}

                    # Add the guild_id to the user's list of guilds if not already there
                    user_id = str(user_id)
                    if user_id not in user_data:
                        user_data[user_id] = [guild_id]
                    elif guild_id not in user_data[user_id]:
                        user_data[user_id].append(guild_id)

                    # Save the updated data to the JSON file
                    with open(json_file, 'w') as f:
                        json.dump(user_data, f, indent=4)

                else:
                    # The attachment is not a PNG or JPEG file
                    await ctx.send("Please attach a **PNG** or **JPEG** file.")
        except KeyError:
            await ctx.send("**Please set the authorized roles first with `addrole` before adding an OC.**")

    @commands.hybrid_command(name='ocdelete', with_app_command=True)
    async def ocdelete(self, ctx: CustomContext):
        """ Delete an oc from the database """
        # Get guild and user role
        guild_id = str(ctx.guild.id)
        user_roles = extract_role_ids(ctx.author.roles)  # Helper function to get role IDs
        user_id = ctx.author.id

        # Load roles from JSON (assume `open_json()` loads `roles.json`)
        self.roles_dict = open_json()

        try:
            # Check if permissions have been set for the server
            roles_list = self.roles_dict[guild_id]
            # Verify if the user is allowed to access the database
            if not any(str(role) in roles_list for role in user_roles):
                await ctx.send("You do not have permission to access the database.")
                return

            matching_ids = await self.find_matching_id(guild_id)

            if str(user_id) not in matching_ids:
                await ctx.send("You have no characters registered in the database.")
                return

            template_name = await self.selectTemplate()
            # Fetch all OCs for the user across all templates
            all_ocs = []
            for table in template_name:
                ocs = await self.bot.pool.fetch(f'SELECT character_name FROM {table} WHERE user_id = $1 AND guild_id = $2',
                                                str(user_id), guild_id)
                all_ocs.extend([row['character_name'] for row in ocs])

            if not all_ocs:
                await ctx.send("You have no OCs in the database to delete.")
                return
            # Display dropdown to select OC
            oc_delete_view = MyView(labels=all_ocs, values=all_ocs, bot=self.bot, use_modal=False)
            await ctx.send(content="**Select the OC to delete**:", view=oc_delete_view)
            await oc_delete_view.wait()  # Wait for the user to make a selection

            if oc_delete_view.value:
                selected_oc = oc_delete_view.value
                # Delete the selected OC from the appropriate table
                for table in template_name:
                    query = f'DELETE FROM {table} WHERE character_name = ? AND user_id = ?'
                    result = await self.bot.pool.execute(
                        query, selected_oc, str(user_id))
                    if result == "DELETE 1":  # Stop if OC was found and deleted
                        await ctx.send(f"OC **{selected_oc}** has been successfully deleted.")
                        return

                await ctx.send(f"Could not find OC **{selected_oc}** to delete. It may have been deleted already.")
            else:
                await ctx.send("You did not select an OC for deletion.")

        except KeyError:
            await ctx.send("Roles for this server have not been set. Please use the `addrole` command first.")

    @commands.hybrid_command(name='ocmodify', with_app_command=True)
    async def ocmodify(self, ctx: CustomContext):
        """ Modify OC in the database with respect to user and guild id """
        """ Delete an oc from the database """
        # Get guild and user role
        guild_id = str(ctx.guild.id)
        user_roles = extract_role_ids(ctx.author.roles)  # Helper function to get role IDs
        user_id = ctx.author.id

        # Load roles from JSON (assume `open_json()` loads `roles.json`)
        self.roles_dict = open_json()

        try:
            # Check if permissions have been set for the server
            roles_list = self.roles_dict[guild_id]
            # Verify if the user is allowed to access the database
            if not any(str(role) in roles_list for role in user_roles):
                await ctx.send("You do not have permission to access the database.")
                return

            matching_ids = await self.find_matching_id(guild_id)

            if str(user_id) not in matching_ids:
                await ctx.send("You have no characters registered in the database.")
                return

            template_name = await self.selectTemplate()
            # Fetch all OCs for the user across all templates
            all_ocs = []
            for table in template_name:
                ocs = await self.bot.pool.fetch(
                    f'SELECT character_name FROM {table} WHERE user_id = $1 AND guild_id = $2',
                    str(user_id), guild_id)
                all_ocs.extend([row['character_name'] for row in ocs])

            if not all_ocs:
                await ctx.send("You have no OCs in the database to delete.")
                return
            # Display dropdown to select OC
            oc_modify = MyView(labels=all_ocs, values=all_ocs, bot=self.bot, use_modal=False)
            await ctx.send(content="**Select the OC to delete**:", view=oc_modify)
            await oc_modify.wait()  # Wait for the user to make a selection

            if oc_modify.value:
                selected_oc = oc_modify.value
                # TODO Modal logic implementation

            else:
                await ctx.send("You did not select an OC for deletion.")

        except KeyError:
            await ctx.send("Roles for this server have not been set. Please use the `addrole` command first.")

    @commands.hybrid_command(name='oclist', with_app_command=True)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def oclist(self, ctx: CustomContext):
        """ List all oc of an artist for the current server """
        guild_id = str(ctx.guild.id)

        matching_user_ids = await self.find_matching_id(guild_id)
        # If there are no matching users
        if not matching_user_ids:
            await ctx.send("No users found with the current guild.")
            return

        else:
            print(matching_user_ids)
            # Fetch usernames for the matching user_ids
            user_names = []
            for user_id in matching_user_ids:
                user = await self.bot.fetch_user(user_id)
                if user:
                    user_names.append(user.name)

            # Send the list of matching user_ids (or process them further as needed)
            artist_selector = MyView(labels=user_names, values=matching_user_ids, bot=self.bot, use_modal=False)
            await ctx.send(content='**Select the artist**', view=artist_selector)
            await artist_selector.wait()  # continues after stop() or timeout

            artist_id = artist_selector.value

            # Construct the query string dynamically
            try:
                # Step 1: Get all the table names from the TEMPLATE table
                rows = await self.bot.pool.fetch('SELECT template_name FROM Templates')
                table_names = [row['template_name'] for row in rows]

                # Step 2: For each table name, fetch the OC names for the given artist_id
                oc_names = []
                for table_name in table_names:
                    query = f'SELECT character_name FROM {table_name} WHERE user_id = $1'
                    result = await self.bot.pool.fetch(query, artist_id)
                    oc_names.extend([row['character_name'] for row in result])

                # Return the result
                if oc_names:
                    embed = discord.Embed(
                        title=f"OC List for {self.bot.get_user(int(artist_id))}",
                        description="\n".join(oc_names),
                        color=discord.Colour.dark_embed()
                    )
                    await ctx.send(embed=embed)
                else:
                    await ctx.send(f"No OC names found for artist {self.bot.get_user(int(artist_id))}.")

            except Exception as e:
                await ctx.send(f"An error occurred: {str(e)}")

    @commands.hybrid_command(name='ocinfo', with_app_command=True)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def ocinfo(self, ctx: CustomContext):
        """ Gives the information sheet of an OC """
        guild_id = str(ctx.guild.id)

        matching_user_ids = await self.find_matching_id(guild_id)
        # If there are no matching users
        if not matching_user_ids:
            await ctx.send("No users found with the current guild.")
            return

        else:
            # Fetch usernames for the matching user_ids
            user_names = []
            for user_id in matching_user_ids:
                user = await self.bot.fetch_user(user_id)
                if user:
                    user_names.append(user.name)

            # Send the list of matching user_ids (or process them further as needed)
            artist_selector = MyView(labels=user_names, values=matching_user_ids, bot=self.bot, use_modal=False)
            await ctx.send(content='**Select the artist**', view=artist_selector)
            await artist_selector.wait()  # continues after stop() or timeout

            artist_id = artist_selector.value

            # Construct the query string dynamically
            oc_dict_name = {}
            try:
                # Step 1: Get all the table names from the TEMPLATE table
                rows = await self.bot.pool.fetch('SELECT template_name FROM Templates')
                table_names = [row['template_name'] for row in rows]

                # Step 2: For each table name, fetch the OC names for the given artist_id
                for table_name in table_names:
                    query = f'SELECT character_name FROM {table_name} WHERE user_id = $1'
                    result = await self.bot.pool.fetch(query, artist_id)
                    # Store the results in the dictionary, keyed by the template name
                    oc_dict_name[table_name] = [row['character_name'] for row in result]

                # Step 3: Flatten the dictionary into a list for dropdown
                print(oc_dict_name)
                # Return the result
                if bool(oc_dict_name):  # Empty dictionaries evaluate to False in Python
                    # Send the list of matching oc for given user_id
                    oc_names = concatenate_dict_values(oc_dict_name)  # just need the list of names for this step
                    oc_selector = MyView(labels=oc_names, values=oc_names, bot=self.bot, use_modal=False)
                    await ctx.send(content='**Select the character**', view=oc_selector)
                    await oc_selector.wait()  # continues after stop() or timeout

                    oc_name = oc_selector.value
                    # Fetch information of selected OC
                    table_name = get_key_by_value(value=oc_name, dictionary=oc_dict_name)
                    query_oc_dict = await fetch_oc_information(bot=self.bot, table_name=table_name, character_name=oc_name, user_id=str(artist_id))

                    # Get keys and values from the oc dictionary
                    oc_dict = query_oc_dict.copy()
                    # Get color and picture first
                    color = oc_dict['color']
                    picture_url = oc_dict['picture_url']
                    for e in ['character_id', 'user_id', 'guild_id', 'color', 'picture_url']:
                        oc_dict.pop(e)
                    categories = list(oc_dict.keys())
                    categories_pages = [categories[i:i + 5] for i in range(0, len(categories), 5)]
                    values_pages = [list(oc_dict.values())[i:i + 5] for i in range(0, len(categories), 5)]

                    # TODO Build embed depending on oc selected and template
                    embed_list = []
                    # Attach OC picture to the embed
                    oc_picture_file = discord.File(BytesIO(picture_url), filename="oc_picture.png")

                    for page in range(len(categories_pages)):
                        embed = create_embed(
                            categories=categories_pages[page],
                            values=values_pages[page],
                            color=color
                        )

                        # Add artist pfp as thumbnail
                        artist = ctx.bot.get_user(int(artist_id))
                        avatar_url = artist.avatar
                        embed.set_thumbnail(url=avatar_url)  # Artist avatar

                        embed_list.append(embed)
                        embed.set_image(url=f"attachment://{oc_picture_file.filename}")

                    await PaginatedOCView().start(ctx=ctx, pages=embed_list, file=oc_picture_file)

                else:
                    await ctx.send(f"No OC names found for artist {self.bot.get_user(int(artist_id))}.")

            except Exception as e:
                await ctx.send(f"An error occurred: {str(e)}")

    @commands.hybrid_command(name='ocrandom', with_app_command=True)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def ocrandom(self, ctx: CustomContext):
        """ Send the description of a random selected OC """
        """ Sends a random OC from a selected artist """
        guild_id = str(ctx.guild.id)

        matching_user_ids = await self.find_matching_id(guild_id)
        # If there are no matching users
        if not matching_user_ids:
            await ctx.send("No users found with the current guild.")
            return

        else:
            # Randomly select a user_id from the matching_user_ids list
            artist_id = random.choice(matching_user_ids)

            # Construct the query string dynamically for fetching OC names
            oc_dict = {}
            try:
                # Step 1: Get all the table names from the TEMPLATE table
                rows = await self.bot.pool.fetch('SELECT template_name FROM Templates')
                table_names = [row['template_name'] for row in rows]

                # Step 2: For each table name, fetch the OC names for the selected artist_id
                for table_name in table_names:
                    query = f'SELECT character_name, description FROM {table_name} WHERE user_id = $1'
                    result = await self.bot.pool.fetch(query, artist_id)
                    # Store the results in the dictionary, keyed by the template name
                    oc_dict[table_name] = [(row['character_name'], row['description']) for row in result]

                # Step 3: Flatten the dictionary into a list of OCs
                if oc_dict:
                    oc_names = []
                    for template_name, ocs in oc_dict.items():
                        oc_names.extend([oc[0] for oc in ocs])

                    # Randomly select an OC from the list
                    random_oc_name = random.choice(oc_names)

                    # Find the template and description for the selected OC
                    for template_name, ocs in oc_dict.items():
                        for oc_name, description in ocs:
                            if oc_name == random_oc_name:
                                # Send the OC details (name, description, template name)
                                embed = discord.Embed(
                                    title=f"OC Information: {random_oc_name}",
                                    description=f"**Template:** {template_name}",
                                    color=discord.Colour.blue()
                                )
                                await ctx.send(embed=embed)
                                break
                else:
                    await ctx.send("No OC names found for the selected artist.")
            except Exception as e:
                await ctx.send(f"An error occurred: {str(e)}")






async def setup(bot):
    await bot.add_cog(OcManager(bot))

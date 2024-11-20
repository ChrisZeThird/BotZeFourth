import asyncio
import discord
import json
import os

from discord.ext import commands
from utils.data import DiscordBot
from utils.default import CustomContext
from utils.embed import init_embed
from utils.misc import extract_role_ids, open_json
from utils.picker import ColorPicker, MyView


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
                    rows = await self.bot.pool.fetch('SELECT * FROM Templates')
                    template_names = [row['template_name'] for row in rows]
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

    # @commands.hybrid_command(name='ocdelete', with_app_command=True)
    # @is_role_setup()
    # async def ocdelete(self, ctx: CustomContext):
    #     """ Delete an oc from the database """
    #
    # @commands.hybrid_command(name='ocmodify', with_app_command=True)
    # @is_role_setup()
    # async def ocmodify(self, ctx: CustomContext):
    #     """ Modify OC in the database with respect to user and guild id """
    #
    @commands.hybrid_command(name='oclist', with_app_command=True)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def oclist(self, ctx: CustomContext):
        """ List all oc of an artist for the current server """
        guild_id = str(ctx.guild.id)

        # Step 1: Get all the template names from the Templates table
        rows = await self.bot.pool.fetch('SELECT template_name FROM Templates')
        table_names = [row['template_name'] for row in rows]

        # Step 2: Find user_ids from all tables where guild_id matches the current guild
        matching_user_ids = set()
        for table_name in table_names:
            query = f'SELECT DISTINCT user_id FROM {table_name} WHERE guild_id = $1'
            result = await self.bot.pool.fetch(query, guild_id)
            matching_user_ids.update(row['user_id'] for row in result)

        # If there are no matching users
        if not matching_user_ids:
            await ctx.send("No users found with the current guild.")
            return

        else:
            # Step 3: Fetch usernames for the matching user_ids
            print(matching_user_ids)
            user_names = []
            for user_id in matching_user_ids:
                user = await self.bot.fetch_user(user_id)
                user_names.append(user.name if user else f"Unknown User ({user_id})")

            print(user_names)
            # Send the list of matching user_ids (or process them further as needed)
            artist_selector = MyView(labels=user_names, values=matching_user_ids, bot=self.bot, use_modal=False)
            await ctx.send(content='**Select the artist**', view=artist_selector)
            await artist_selector.wait()  # continues after stop() or timeout

            artist_id = artist_selector.value
            print(artist_id)

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

                # Step 3: Return the result
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

            # query = f"FROM INTO {template} ({', '.join(columns)}) VALUES ({placeholders})"
            # # Execute the query
            # print(await self.bot.pool.execute(query, *values))

    #
    # @commands.hybrid_command(name='artistlist', with_app_command=True)
    # @commands.cooldown(1, 60, commands.BucketType.user)
    # async def artistlist(self, ctx: CustomContext):
    #     """ List all artists of a server """
    #
    # @commands.hybrid_command(name='ocrandom', with_app_command=True)
    # @commands.cooldown(1, 30, commands.BucketType.user)
    # async def ocrandom(self, ctx: CustomContext):
    #     """ Send the description of a random selected OC """
    #
    # @commands.hybrid_command(name='ocinfo', with_app_command=True)
    # @commands.cooldown(1, 30, commands.BucketType.user)
    # async def ocinfo(self, ctx: CustomContext, artist_name, oc_name):
    #     """ Gives the information sheet of an OC """


async def setup(bot):
    await bot.add_cog(OcManager(bot))

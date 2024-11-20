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
        """ List all oc of an artist """


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

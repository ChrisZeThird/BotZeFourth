import asyncio
import discord
import json
import os

from discord.ext import commands
from utils.data import DiscordBot
from utils.default import CustomContext
from utils.embed import init_embed
from utils.misc import extract_role_ids
from utils.picker import ColorPicker, MyView


class OcManager(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot
        self.roles_dic = self.load_roles()

    def load_roles(self, file_path="roles.json"):
        """
        Load roles from JSON file, if file does not exist file is created and dumped with empty dictionary.
        :return:
        """
        try:
            with open(file_path, "r") as file:
                return json.load(file)
        except FileNotFoundError:
            # Create the file with an empty dictionary if it doesn't exist
            with open(file_path, "w") as file:
                json.dump({}, file)
            return {}

    def is_role_setup(self):
        """
        :return: Bool
        """
        async def predicate(ctx):
            # Get guild and user roles
            guild_id = str(ctx.guild.id)

            if guild_id not in self.roles_dic:
                await ctx.send(
                    "No roles have been allowed to use this command, contact your local admins if you think this is a mistake.")
                return False
            else:
                guild_roles_list = self.roles_dict[guild_id]
                user_roles = extract_role_ids(
                    ctx.message.author.roles)  # roles formatting needed to only keep the actual id

                if set(map(str, user_roles)) & set(guild_roles_list):
                    return True

                await ctx.send(
                    "You are not allowed to use this command. If you think this is a mistake, contact your local admins.")
                return False

        return commands.check(predicate)

    @commands.hybrid_command(name='ocadd', with_app_command=True)
    @is_role_setup()
    async def ocadd(self, ctx, picture: discord.Attachment):
        """
        Add OC to the database with respect to user and guild id
        """
        # Get guild and user role
        guild_id = str(ctx.guild.id)
        user_id = ctx.message.author.id
        user_name = ctx.message.author.name

        if picture.content_type in ['image/png', 'image/jpeg']:
            def check(m):
                return m.author == ctx.author

            # Select the Template
            rows = await self.bot.pool.fetch("SELECT template_name FROM Templates;")
            template_names = [row['template_name'] for row in rows]

            # Create an instance of the DropdownMenu view for the oc names
            template_selector = MyView(labels=template_names, values=template_names)
            await ctx.send(content='**Select the OC to modify**', view=template_selector)
            await template_selector.wait()  # continues after stop() or timeout
            selected_template = template_selector.value

            # Create instance of Modal to get user input for the OC as a form
            # Forms entries depends on the template used
            # TODO Find a way to account for long template entry list to have different form
            # TODO Button to confirm entry to then call for the next modal
            # TODO Loop to create the form

            # Create instance of the ColorPicker DropdownMenu view
            view = ColorPicker(bot=self.bot)
            await ctx.send(view=view)
            await view.wait()

            colour = view.colour
            await ctx.send(f'You have picked {colour} for your OC!')

            # Prepare the picture to be stored in the database
            oc_picture = await picture.read()

        else:
            # The attachment is not a PNG or JPEG file
            await ctx.send("Please attach a **PNG** or **JPEG** file.")

    @commands.hybrid_command(name='ocdelete', with_app_command=True)
    @is_role_setup()
    async def ocdelete(self, ctx: CustomContext):
        """ Delete an oc from the database """

    @commands.hybrid_command(name='ocmodify', with_app_command=True)
    @is_role_setup()
    async def ocmodify(self, ctx: CustomContext):
        """ Modify OC in the database with respect to user and guild id """

    @commands.hybrid_command(name='oclist', with_app_command=True)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def oclist(self, ctx: CustomContext, artist_name):
        """ List all oc of an artist """

    @commands.hybrid_command(name='artistlist', with_app_command=True)
    @commands.cooldown(1, 60, commands.BucketType.user)
    async def artistlist(self, ctx: CustomContext):
        """ List all artists of a server """

    @commands.hybrid_command(name='ocrandom', with_app_command=True)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def ocrandom(self, ctx: CustomContext):
        """ Send the description of a random selected OC """

    @commands.hybrid_command(name='ocinfo', with_app_command=True)
    @commands.cooldown(1, 30, commands.BucketType.user)
    async def ocinfo(self, ctx: CustomContext, artist_name, oc_name):
        """ Gives the information sheet of an OC """


async def setup(bot):
    await bot.add_cog(OcManager(bot))

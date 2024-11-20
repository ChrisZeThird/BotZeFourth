import asyncio
import discord
import json
import os

from discord.ext import commands
from utils.data import DiscordBot
from utils.default import CustomContext
from utils.embed import init_embed
from utils.misc import extract_role_ids
from utils.picker import ColorPicker, MyView, ConfirmButton
from utils.form import DynamicFormModal, CompactAbilityModal, MyModal


class OcManager(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot
        self.roles_dic = self.load_roles()
        self.exclude_fields = ["picture_url", "color", "template_id"]

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
                guild_roles_list = self.roles_dic[guild_id]
                user_roles = extract_role_ids(
                    ctx.message.author.roles)  # roles formatting needed to only keep the actual id

                if set(map(str, user_roles)) & set(guild_roles_list):
                    return True

                await ctx.send(
                    "You are not allowed to use this command. If you think this is a mistake, contact your local admins.")
                return False

        return commands.check(predicate)

    @commands.hybrid_command(name='ocadd', with_app_command=True)
    # @is_role_setup(roles_dic)
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
            rows = await self.bot.pool.fetch('SELECT * FROM Templates')
            template_names = [row['template_name'] for row in rows]

            # Create an instance of the DropdownMenu view for the oc names
            template_selector = MyView(labels=template_names, values=template_names)
            await ctx.send(content='**Select the template to use**', view=template_selector)
            await template_selector.wait()  # continues after stop() or timeout
            selected_template = template_selector.value

            # Retrieve columns for the selected template
            query = f"PRAGMA table_info({selected_template})"
            columns = await self.bot.pool.fetch(query)
            column_names = [row['name'] for row in columns]

            # Skip DB-related fields and chunk columns for modal fields
            user_fields = column_names[2:]  # Assuming first 2 are DB info
            if selected_template != "DnDCharacters":
                user_fields = [field for field in user_fields if field not in self.exclude_fields]
                field_chunks = [user_fields[i:i + 5] for i in range(0, len(user_fields), 5)]

            else:
                # Custom handling for DnDCharacters template
                ability_scores = ["strength", "dexterity", "constitution", "intelligence", "wisdom", "charisma"]
                ability_modifiers = ["str_mod", "dex_mod", "con_mod", "int_mod", "wis_mod", "cha_mod"]

                # Split fields into chunks of 5 for modals
                user_fields = [field for field in user_fields if field not in ability_scores + ability_modifiers + self.exclude_fields]
                field_chunks = [user_fields[i:i + 5] for i in range(0, len(user_fields), 5)] + ability_scores + ability_modifiers
                print("DND setup")
                ability_modal = CompactAbilityModal()
                await ctx.send_modal(ability_modal)
                await ability_modal.wait()  # Wait for the modal to complete
                ability_data = ability_modal.ability_data
            print(f"Field chunks for modal: {field_chunks}")

            # Loop through chunks and display modals
            # collected_data = {}
            # for chunk in field_chunks:
            #     modal = DynamicFormModal(title=f"{selected_template} Form", fields=chunk,
            #                              template_name=selected_template)
            #     await ctx.send_modal(modal)
            #     # await modal.wait()  # Wait for the modal to complete
            #     collected_data.update(modal.user_inputs)
            #
            # await ctx.send(f"Collected data: {collected_data}")

            # Create instance of Modal to get user input for the OC as a form

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
    # @commands.hybrid_command(name='oclist', with_app_command=True)
    # @commands.cooldown(1, 30, commands.BucketType.user)
    # async def oclist(self, ctx: CustomContext, artist_name):
    #     """ List all oc of an artist """
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

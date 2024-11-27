import asyncio
import discord
import json
import os
import sqlite3

from utils import permissions
from utils.default import CustomContext
from discord.ext import commands
from utils.data import DiscordBot
from utils.misc import open_json, save_dict
from utils.picker import MyView


# Function to generate an embed listing the roles or channels
def listing_embed(title, items):
    embed = discord.Embed(title=title)
    if not items:
        embed.add_field(name="No items", value="There are no roles/channels to display.", inline=False)
    else:
        for item in items:
            embed.add_field(name=item, inline=False)
    return embed


class Admin(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot

    @commands.hybrid_command(name='serverslist', with_app_command=True)
    @commands.is_owner()
    async def serverslist(self, ctx):
        """ Give the list of servers where the bot is on (only for bot owner) """
        servers = list(self.bot.guilds)
        # print(servers)
        await ctx.send(f"Connected on {str(len(servers))} servers:")
        await ctx.send('\n'.join(guild.name for guild in servers))

    @commands.hybrid_command(name='leaveserver', with_app_command=True)
    @commands.is_owner()
    async def leaveserver(self, ctx, server_id):
        """ Leave a server with its id given as argument, only available to bot owner"""
        guild = await self.bot.fetch_guild(server_id)
        print(guild)
        await guild.leave()
        await ctx.send(f"Left server {guild.name}")

    @commands.hybrid_command(name='addrole', with_app_command=True)
    @commands.has_permissions(manage_roles=True)
    async def addrole(self, ctx: CustomContext, role):
        """ Add roles allowed to use the bot"""
        # Check if the JSON file exists
        roles_dict = open_json()
        guild_id = str(ctx.guild.id)
        if guild_id not in roles_dict:
            roles_dict[guild_id] = []

        if role not in roles_dict[guild_id]:
            try:
                role_id = int(role)
                role_object = discord.utils.get(ctx.guild.roles, id=role_id)  # Check if role exists in the guild

                if role_object is None:
                    await ctx.send("❌ **No role found with that ID. Please try again with a valid Role ID.**")

                else:
                    roles_dict[guild_id].append(role)
                    await save_dict(file="roles.json", d=roles_dict)
                    print('test')
                    await ctx.send(f"✅ Role **{role_object.name}** added successfully!")

            except ValueError:
                await ctx.send("❌ **Invalid role ID. Please provide a valid number.**")
                return

        else:
            await ctx.send('**⚠️ Role already allowed to use BotZeFourth database system.**')

    @commands.hybrid_command(name='removerole', with_app_command=True)
    @commands.has_permissions(manage_roles=True)
    async def removerole(self, ctx: CustomContext):
        """ Remove roles allowed to use the bot"""
        # Check if the JSON file exists
        roles_dict = open_json()

        # Get server ID
        guild_id = str(ctx.guild.id)

        if guild_id in roles_dict:
            # Generate and send embed listing all channels
            roles_list = roles_dict.get(guild_id, [])

            if len(roles_list) > 0:
                roles_names = [discord.utils.get(ctx.guild.roles, id=int(role_id)).name for role_id in roles_list]

                # Send the list of roles setup
                roles_selector = MyView(labels=roles_names, values=roles_list, bot=self.bot, use_modal=False)
                await ctx.send(content='**Select the role to remove**', view=roles_selector)
                await roles_selector.wait()  # continues after stop() or timeout

                role = roles_selector.value
                roles_dict[guild_id].remove(role)

                await save_dict(file="roles.json", d=roles_dict)
                await ctx.send(f"✅ Role successfully removed!")

            else:
                await ctx.send("⚠️ No role was found for your server. Please add one first.")

        else:
            await ctx.send("**⚠️ Please first add role before trying to remove any.**")

    @commands.hybrid_command(name='addchannel', with_app_command=True)
    @commands.has_permissions(manage_channels=True)
    async def addchannel(self, ctx: CustomContext, channel_id):
        # Check if the JSON file exists
        channels_dict = open_json(path='channels.json')

        # Get the server ID
        guild_id = str(ctx.guild.id)
        # Get channel object to ensure user input an actual channel
        channel = self.bot.get_channel(int(channel_id))

        if guild_id not in channels_dict:
            channels_dict[guild_id] = []

        if channel:
            # Make sure the dictionary is set up before adding a channel

            if channel_id not in channels_dict[guild_id]:
                channels_dict[guild_id].append(channel_id)
                await save_dict(file="channels.json", d=channels_dict)
                await ctx.send(f"✅ Channel {channel.mention} has been added.")

        else:
            await ctx.send("❌ Invalid channel ID.")

    @commands.hybrid_command(name='removechannel', with_app_command=True)
    @commands.has_permissions(manage_channels=True)
    async def removechannel(self, ctx: CustomContext):
        """ Remove roles allowed to use the bot"""
        # Check if the JSON file exists
        channels_dict = open_json(path='channels.json')

        # Get the server ID
        guild_id = str(ctx.guild.id)
        # Make sure the dictionary is set up before removing a channel
        if guild_id not in channels_dict:
            channels_dict[guild_id] = []
            await ctx.send("⚠️ No channels have been added yet.")

        else:
            channels_list = channels_dict.get(guild_id, [])

            if len(channels_list) > 0:
                channel_names = [ctx.guild.get_channel(int(c)).name for c in channels_list]
                # Send the list of channels setup
                channel_selector = MyView(labels=channel_names, values=channels_list, bot=self.bot, use_modal=False)
                await ctx.send(content='**Select the channel to remove**', view=channel_selector)
                await channel_selector.wait()  # continues after stop() or timeout
                channel_id = channel_selector.value

                # Get channel object to ensure user input an actual channel
                channel = self.bot.get_channel(int(channel_id))

                if channel:
                    channels_dict[guild_id].remove(channel_id)
                    await save_dict(file="channels.json", d=channels_dict)
                    await ctx.send(f"✅ Channel {channel.mention} has been deleted.")

                else:
                    await ctx.send("⚠️ No channel ID was found. Please add one first.")

            else:
                await ctx.send("⚠️ No channel has been added yet.")

    @commands.hybrid_command(name='sendmessage', with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def sendmessage(self, ctx: CustomContext, channel_id, message_to_send):
        channel = self.bot.get_channel(int(channel_id))
        await channel.send(message_to_send)
        await ctx.send('Message was successfully delivered')

    @commands.hybrid_command(name='makeinvite', with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def makeinvite(self, ctx, channel_id: discord.abc.GuildChannel = None):
        """
        Generates an invitation link for any server the bot is in.

        Parameters:
        channel: The ID of channel you want to generate an invitation for. If not provided, it will use the current channel where command was used.
        """
        if channel_id is None:
            invite = await ctx.channel.create_invite(max_uses=1, unique=True)
            await ctx.send(invite)
        else:
            invite = await channel_id.create_invite(max_uses=1, unique=True)
            await ctx.send(invite)

    @commands.hybrid_command(name='listmembers', with_app_command=True)
    @commands.has_permissions(administrator=True)
    async def listmembers(self, ctx, server_id = None):
        """
        Make a list of all discord members for a given Guild

        :param ctx:
        :param server_id:
        :return:
        """
        embed = discord.Embed(title="Member List", color=discord.Color.blue())
        guild_to_check = ctx.guild if server_id is None else self.bot.get_guild(int(server_id))

        member_list = "\n".join([f'{member.name} (ID: {member.id})' for member in guild_to_check.members])
        embed.description = f"Members of {guild_to_check.name}:\n{member_list}"

        await ctx.send(embed=embed)


async def setup(bot):
    await bot.add_cog(Admin(bot))

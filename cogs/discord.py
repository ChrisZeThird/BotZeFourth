import discord

from io import BytesIO
from utils import default
from utils.default import CustomContext
from discord.ext import commands
from utils.data import DiscordBot


class DiscordInfo(commands.Cog):
    def __init__(self, bot):
        self.bot: DiscordBot = bot

    @commands.command(aliases=["av", "pfp"])
    @commands.guild_only()
    async def avatar(self, ctx: CustomContext, *, user: discord.Member = None):
        """ Get the avatar of you or someone else """
        user = user or ctx.author

        avatars_list = []

        def target_avatar_formats(target):
            formats = ["JPEG", "PNG", "WebP"]
            if target.is_animated():
                formats.append("GIF")
            return formats

        if not user.avatar and not user.guild_avatar:
            return await ctx.send(f"**{user}** has no avatar set, at all...")

        if user.avatar:
            avatars_list.append("**Account avatar:** " + " **-** ".join(
                f"[{img_format}]({user.avatar.replace(format=img_format.lower(), size=1024)})"
                for img_format in target_avatar_formats(user.avatar)
            ))

        embed = discord.Embed(colour=user.top_role.colour.value)

        if user.guild_avatar:
            avatars_list.append("**Server avatar:** " + " **-** ".join(
                f"[{img_format}]({user.guild_avatar.replace(format=img_format.lower(), size=1024)})"
                for img_format in target_avatar_formats(user.guild_avatar)
            ))
            embed.set_thumbnail(url=user.avatar.replace(format="png"))

        embed.set_image(url=f"{user.display_avatar.with_size(256).with_static_format('png')}")
        embed.description = "\n".join(avatars_list)

        await ctx.send(f"🖼 Avatar of **{user}**", embed=embed)

    @commands.command()
    @commands.guild_only()
    async def roles(self, ctx: CustomContext):
        """ Get all roles in current server """
        allroles = ""

        for num, role in enumerate(sorted(ctx.guild.roles, reverse=True), start=1):
            allroles += f"[{str(num).zfill(2)}] {role.id}\t{role.name}\t[ Users: {len(role.members)} ]\r\n"

        data = BytesIO(allroles.encode("utf-8"))
        await ctx.send(content=f"Roles in **{ctx.guild.name}**",
                       file=discord.File(data, filename=f"{default.timetext('Roles')}"))

    @commands.command(aliases=["joined"])
    @commands.guild_only()
    async def joindate(self, ctx: CustomContext, *, user: discord.Member = None):
        """ Check when a user joined the current server """
        user = user or ctx.author
        await ctx.send("\n".join([
            f"**{user}** joined **{ctx.guild.name}**",
            f"{default.date(user.joined_at, ago=True)}"
        ]))


async def setup(bot):
    await bot.add_cog(DiscordInfo(bot))

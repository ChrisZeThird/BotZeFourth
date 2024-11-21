from __future__ import annotations

import discord
from discord.ui import Button, View
from discord.ext import commands

from io import BytesIO
from typing import Callable, Optional


def create_embed(categories: list, values: list, color: str) -> discord.Embed:
    """
    Create a Discord embed with categories as field names and values as field values.


    :param categories: List of strings for the field names.
    :param values: List of strings for the field values.
    :param color: Hex color code as a string (e.g., "#FF5733").

    Returns:
        discord.Embed: A Discord embed with the specified fields and color.
    """
    # Convert the color string to a Discord-compatible integer
    try:
        embed_color = discord.Color(int(color.lstrip("#"), 16))
    except ValueError:
        raise ValueError("Invalid color format. Please provide a hex color code (e.g., '#FF5733').")

    # Ensure categories and values have the same length
    if len(categories) != len(values):
        raise ValueError("The 'categories' and 'values' lists must have the same length.")

    # Create the embed
    embed = discord.Embed(title='OC Information', color=embed_color)

    # Add fields to the embed
    for category, value in zip(categories, values):
        embed.add_field(name=category, value=value, inline=False)

    return embed


class PaginatedOCView(View):
    def __init__(self,
                 timeout: int = 60,
                 PreviousButton: discord.ui.Button = discord.ui.Button(emoji=discord.PartialEmoji(name="\U000025c0")),
                 NextButton: discord.ui.Button = discord.ui.Button(emoji=discord.PartialEmoji(name="\U000025b6")),
                 PageCounterStyle: discord.ButtonStyle = discord.ButtonStyle.grey,
                 InitialPage: int = 0, AllowExtInput: bool = False,
                 ephemeral: bool = False) -> None:
        # Init values
        self.PreviousButton = PreviousButton
        self.NextButton = NextButton
        self.PageCounterStyle = PageCounterStyle
        self.InitialPage = InitialPage
        self.AllowExtInput = AllowExtInput
        self.ephemeral = ephemeral

        self.pages = None
        self.ctx = None
        self.message = None
        self.current_page = None
        self.page_counter = None
        self.total_page_count = None

        super().__init__(timeout=timeout)

    async def start(self, ctx: discord.Interaction | commands.Context, pages: list[discord.Embed], file):

        if isinstance(ctx, discord.Interaction):
            ctx = await commands.Context.from_interaction(ctx)

        self.pages = pages
        self.total_page_count = len(pages)
        self.ctx = ctx
        self.current_page = self.InitialPage

        self.PreviousButton.callback = self.previous_button_callback
        self.NextButton.callback = self.next_button_callback

        self.page_counter = SimplePaginatorPageCounter(style=self.PageCounterStyle,
                                                       TotalPages=self.total_page_count,
                                                       InitialPage=self.InitialPage)

        self.add_item(self.PreviousButton)
        self.add_item(self.page_counter)
        self.add_item(self.NextButton)

        self.message = await ctx.send(file=file, embed=self.pages[self.InitialPage], view=self, ephemeral=self.ephemeral)

    async def previous(self):
        if self.current_page == 0:
            self.current_page = self.total_page_count - 1
        else:
            self.current_page -= 1

        self.page_counter.label = f"{self.current_page + 1}/{self.total_page_count}"
        await self.message.edit(embed=self.pages[self.current_page], view=self)

    async def next(self):
        if self.current_page == self.total_page_count - 1:
            self.current_page = 0
        else:
            self.current_page += 1

        self.page_counter.label = f"{self.current_page + 1}/{self.total_page_count}"
        await self.message.edit(embed=self.pages[self.current_page], view=self)

    async def next_button_callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author and self.AllowExtInput:
            embed = discord.Embed(description="You cannot control this pagination because you did not execute it.",
                                  color=discord.Colour.red())
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        await self.next()
        await interaction.response.defer()

    async def previous_button_callback(self, interaction: discord.Interaction):
        if interaction.user != self.ctx.author and self.AllowExtInput:
            embed = discord.Embed(description="You cannot control this pagination because you did not execute it.",
                                  color=discord.Colour.red())
            return await interaction.response.send_message(embed=embed, ephemeral=True)
        await self.previous()
        await interaction.response.defer()


class SimplePaginatorPageCounter(discord.ui.Button):
    def __init__(self, style: discord.ButtonStyle, TotalPages, InitialPage):
        super().__init__(label=f"{InitialPage + 1}/{TotalPages}", style=style, disabled=True)

from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from .errors import ProcessingPreviousCommand

if TYPE_CHECKING:
    from ...bot import SGRBOT


class Moderator(commands.Cog):
    def __init__(self, bot: SGRBOT) -> None:
        self.bot = bot
        self.is_deleting: bool = False

    def create_deleting_embed(self) -> discord.Embed:
        deleting_messages_embed = discord.Embed(title="Currently processing the previous `/delmsg command`.",
                                                description="Please try again later.",
                                                color=discord.Color.red())
        return deleting_messages_embed

    @app_commands.command()
    async def delmsg(self, interaction: discord.Interaction, number: app_commands.Range[int, 1, 100]) -> None:
        if self.is_deleting:
            raise ProcessingPreviousCommand

        # Set is_deleting to True to prevent executing another delmsg command while deleting messages
        self.is_deleting = True
        await interaction.response.defer()
        await interaction.delete_original_response()
        await interaction.channel.purge(limit=number)
        # Set is_deleting to False to allow executing another delmsg command
        self.is_deleting = False

    @delmsg.error
    async def delmsg_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        if isinstance(error, ProcessingPreviousCommand):
            deleting_messages_embed = self.create_deleting_embed()
            await interaction.response.send_message(embed=deleting_messages_embed)
            return

        raise error

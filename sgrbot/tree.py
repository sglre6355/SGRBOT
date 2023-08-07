from __future__ import annotations

from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.app_commands import AppCommandError

from .utils import ErrorEmbed

if TYPE_CHECKING:
    from .bot import SGRBOT

class CommandTree(app_commands.CommandTree):
    def __init__(self, bot: SGRBOT, *, fallback_to_global: bool = True) -> None:
        super().__init__(bot, fallback_to_global=fallback_to_global)

    async def on_error(self, interaction: discord.Interaction, error: AppCommandError, /) -> None:
        await super().on_error(interaction, error)

        if isinstance(error, app_commands.CommandInvokeError):
            command_invoke_error_embed = ErrorEmbed(error.original)
            await interaction.response.send_message(embed=command_invoke_error_embed)
            return

        raise error

from __future__ import annotations

import traceback
from typing import TYPE_CHECKING

import discord
import toml

if TYPE_CHECKING:
    from typing import Any


def load_config_file(path: str, mode: str = "r") -> dict[str, Any]:
    with open(path, mode) as f:
        return toml.load(f)

class ErrorEmbed(discord.Embed):
    def __init__(self, error: Exception) -> None:
        error_name = type(error).__name__
        error_log = traceback.format_exc()
        super().__init__(title=f"Command raised an exception `{error_name}`", description=f"```{error_log}```", color=discord.Color.red())

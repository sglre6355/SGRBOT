from __future__ import annotations

import os
from typing import Optional

import discord
from discord.ext import commands

from .utils import load_config_file


class SGRBOT(commands.Bot):
    def __init__(self) -> None:
        super().__init__(command_prefix="", help_command=None, intents=discord.Intents.all())

        self.config = load_config_file("config/SGRBOT.toml")

        self.registered_guilds: Optional[dict[str, discord.Guild]] = None

    async def setup_hook(self) -> None:
        extensions = [dir_name for dir_name in os.listdir("sgrbot/cogs") if os.path.isfile(f"sgrbot/cogs/{dir_name}/__init__.py")]
        for extension in extensions:
            await self.load_extension(f"sgrbot.cogs.{extension}")

        self.registered_guilds = {guild_name: await self.fetch_guild(guild_properties["id"])
                                  for guild_name, guild_properties in self.config["registered_guilds"].items()}

        for guild in self.registered_guilds.values():
            self.tree.copy_global_to(guild=guild)
            await self.tree.sync(guild=guild)

    async def on_ready(self) -> None:
        print(f"Login successful: {self.user}")
        print(f"User ID: {self.user.id}")
        print(f"discord.py version: {discord.__version__}")
        print("---------------")

    async def process_commands(self, message: discord.Message) -> None:
        pass

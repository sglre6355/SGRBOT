from __future__ import annotations

import datetime
from typing import TYPE_CHECKING

import discord
from discord import app_commands
from discord.ext import commands

from ...utils import load_config_file
from .embeds import MinecraftServerEmbed, MinecraftServerEmbedFormats
from .errors import (InvalidServerName, ServerAlreadyRunning, ServerNotRunning,
                     ServerProcessingPreviousCommand, ServerStartFailed)
from .minecraft_server import MinecraftServer

if TYPE_CHECKING:
    from ...bot import SGRBOT


class MinecraftServerManager(commands.Cog):
    def __init__(self, bot: SGRBOT):
        self.bot = bot
        self.servers: dict[str, MinecraftServer] = {}

        minecraft_configs = load_config_file("config/minecraft.toml", "r")
        self.server_configs = minecraft_configs["servers"]

    minecraft = app_commands.Group(name="minecraft", description="Commands to manage minecraft servers running on Docker.")

    def ensure_server_in_servers(self, server_name: str) -> None:
        server = self.servers.get(server_name)
        if server is None:
            server_config = self.server_configs[server_name]
            server = MinecraftServer(name=server_name,
                                     docker_image_name=server_config["docker_image_name"],
                                     docker_image_tag=server_config["docker_image_tag"],
                                     container_name=server_config["container_name"],
                                     volumes=server_config["volumes"],
                                     ports=server_config["ports"],
                                     environment=server_config["environment"],
                                     address=server_config["address"])
            self.servers[server_name] = server

    def abort_if_invald_server_name(self, server_name: str) -> None:
        if server_name not in self.server_configs.keys():
            raise InvalidServerName(server_name)

    def abort_if_processing_previous_command(self, server: MinecraftServer) -> None:
        if server.is_processing:
            raise ServerProcessingPreviousCommand(server)

    def abort_if_running(self, server: MinecraftServer) -> None:
        if server.is_running():
            raise ServerAlreadyRunning(server)

    def abort_if_not_running(self, server: MinecraftServer) -> None:
        if not server.is_running():
            raise ServerNotRunning(server)

    async def delete_status_interaction_message_if_stored(self, server: MinecraftServer) -> None:
        if server.status_interaction_message is not None:
            await server.status_interaction_message.delete()
            server.status_interaction_message = None

    async def server_name_autocomplete(self, interaction, current) -> list[app_commands.Choice[str]]:
        return [app_commands.Choice(name=server_name, value=server_name) for server_name in self.server_configs.keys() if current.lower() in server_name.lower()]

    @minecraft.command()
    @app_commands.autocomplete(server_name=server_name_autocomplete)
    async def start(self, interaction: discord.Interaction, server_name: str) -> None:
        # Before-server-start checks
        self.abort_if_invald_server_name(server_name)

        self.ensure_server_in_servers(server_name)
        server = self.servers[server_name]

        self.abort_if_processing_previous_command(server)
        self.abort_if_running(server)
        await self.delete_status_interaction_message_if_stored(server)

        # Set is_processing to True to prevent other commands from being run while this one is running
        server.is_processing = True

        starting_embed = MinecraftServerEmbed(MinecraftServerEmbedFormats.starting, server=server)
        await interaction.response.send_message(embed=starting_embed)

        dt = datetime.datetime.utcnow()
        server.start()
        await server.wait_until_ready(dt)

        started_embed = MinecraftServerEmbed(MinecraftServerEmbedFormats.started, server=server)
        server.status_interaction_message = await interaction.edit_original_response(embed=started_embed)

        # Set is_processing to False to allow other commands to be run
        server.is_processing = False

    @minecraft.command()
    @app_commands.autocomplete(server_name=server_name_autocomplete)
    async def stop(self, interaction: discord.Interaction, server_name: str) -> None:
        # Before-server-stop checks
        self.abort_if_invald_server_name(server_name)

        self.ensure_server_in_servers(server_name)
        server = self.servers[server_name]

        self.abort_if_processing_previous_command(server)
        self.abort_if_not_running(server)
        await self.delete_status_interaction_message_if_stored(server)

        # Set is_processing to True to prevent other commands from being run while this one is running
        server.is_processing = True

        stopping_embed = MinecraftServerEmbed(MinecraftServerEmbedFormats.stopping, server=server)
        await interaction.response.send_message(embed=stopping_embed)

        server.stop()

        stopped_embed = MinecraftServerEmbed(MinecraftServerEmbedFormats.stopped, server=server)
        await interaction.edit_original_response(embed=stopped_embed)

        # Set is_processing to False to allow other commands to be run
        server.is_processing = False

    @minecraft.command()
    @app_commands.autocomplete(server_name=server_name_autocomplete)
    async def restart(self, interaction: discord.Interaction, server_name: str) -> None:
        # Before-server-restart checks
        self.abort_if_invald_server_name(server_name)

        self.ensure_server_in_servers(server_name)
        server = self.servers[server_name]

        self.abort_if_processing_previous_command(server)
        self.abort_if_not_running(server)
        await self.delete_status_interaction_message_if_stored(server)

        # Set is_processing to True to prevent other commands from being run while this one is running
        server.is_processing = True

        restarting_embed = MinecraftServerEmbed(MinecraftServerEmbedFormats.restarting, server=server)
        await interaction.response.send_message(embed=restarting_embed)

        dt = datetime.datetime.utcnow()
        server.restart()
        await server.wait_until_ready(dt)

        started_embed = MinecraftServerEmbed(MinecraftServerEmbedFormats.started, server=server)
        server.status_interaction_message = await interaction.edit_original_response(embed=started_embed)

        # Set is_processing to False to allow other commands to be run
        server.is_processing = False

    @start.error
    @stop.error
    @restart.error
    async def minecraft_error(self, interaction: discord.Interaction, error: app_commands.AppCommandError) -> None:
        # Set is_processing to False to allow other commands to be run after an error
        if hasattr(error, "server"):
            error.server.is_processing = False

        if isinstance(error, ServerStartFailed):
            start_failed_embed = MinecraftServerEmbed(MinecraftServerEmbedFormats.start_failed, server=error.server)
            await interaction.edit_original_response(embed=start_failed_embed)
            return

        if isinstance(error, InvalidServerName):
            invalid_server_name_embed = MinecraftServerEmbed(MinecraftServerEmbedFormats.invalid_server_name, server_name=error.server_name)
            await interaction.response.send_message(embed=invalid_server_name_embed)
            return

        if isinstance(error, ServerProcessingPreviousCommand):
            server_processing_embed = MinecraftServerEmbed(MinecraftServerEmbedFormats.server_processing, server=error.server)
            await interaction.response.send_message(embed=server_processing_embed)
            return

        if isinstance(error, ServerAlreadyRunning):
            already_running_embed = MinecraftServerEmbed(MinecraftServerEmbedFormats.already_running, server=error.server)
            await interaction.response.send_message(embed=already_running_embed)
            return

        if isinstance(error, ServerNotRunning):
            not_running_embed = MinecraftServerEmbed(MinecraftServerEmbedFormats.not_running, server=error.server)
            await interaction.response.send_message(embed=not_running_embed)
            return

        raise error


async def setup(bot: SGRBOT) -> None:
    await bot.add_cog(MinecraftServerManager(bot))

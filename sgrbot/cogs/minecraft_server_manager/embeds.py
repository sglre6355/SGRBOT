from __future__ import annotations

from enum import Enum
from typing import TYPE_CHECKING, Optional

import discord

if TYPE_CHECKING:
    from .minecraft_server import MinecraftServer


class MinecraftServerEmbedFormat:
    def __init__(self, *, title: str, description: Optional[str] = None, color: discord.Color, fields: Optional[dict[str, str]] = None) -> None:
        self.title = title
        self.description = description
        self.color = color
        self.fields = fields


class MinecraftServerEmbedFormats(Enum):
    start_failed = MinecraftServerEmbedFormat(title="Failed to start the server.",
                                              description="Please check the server log.",
                                              color=discord.Color.red(),
                                              fields={"Server name": "{server.name}"})

    starting = MinecraftServerEmbedFormat(title="Starting the server...",
                                          description="It may take several minutes for the server to start up.",
                                          color=discord.Color.yellow(),
                                          fields={"Server name": "{server.name}"})

    started = MinecraftServerEmbedFormat(title="Server initialization completed!",
                                         description="Please use the following address to access the server.",
                                         color=discord.Color.green(),
                                         fields={"Server name": "{server.name}", "Server address": "{server.address}"})

    stopping = MinecraftServerEmbedFormat(title="Stopping the server...",
                                          description="Please wait for a moment.",
                                          color=discord.Color.yellow(),
                                          fields={"Server name": "{server.name}"})

    stopped = MinecraftServerEmbedFormat(title="The server stopped.",
                                         color=discord.Color.green(),
                                         fields={"Server name": "{server.name}"})

    restarting = MinecraftServerEmbedFormat(title="Restarting the server...",
                                            description="Please wait for a moment.",
                                            color=discord.Color.yellow(),
                                            fields={"Server name": "{server.name}"})

    invalid_server_name = MinecraftServerEmbedFormat(title="The specified server `{server_name}` is invalid.",
                                                     description="Please check the server name and try again.",
                                                     color=discord.Color.red())

    already_running = MinecraftServerEmbedFormat(title="The server specified is already running.",
                                                 color=discord.Color.red(),
                                                 fields={"Server name": "{server.name}"})

    not_running = MinecraftServerEmbedFormat(title="The server specified is not running.",
                                             color=discord.Color.red(),
                                             fields={"Server name": "{server.name}"})

    server_processing = MinecraftServerEmbedFormat(title="The server specified is currently processing the previous command.",
                                                   description="Please wait until the previous action is completed.",
                                                   color=discord.Color.red(),
                                                   fields={"Server name": "{server.name}"})


class MinecraftServerEmbed(discord.Embed):
    def __init__(self, embed_properties: MinecraftServerEmbedFormats, *, server_name: Optional[str] = None, server: Optional[MinecraftServer] = None) -> None:
        if embed_properties.value.title:
            title = embed_properties.value.title.format(server_name=server_name, server=server)
        else:
            title = embed_properties.value.title

        if embed_properties.value.description:
            description = embed_properties.value.description.format(server_name=server_name, server=server)
        else:
            description = embed_properties.value.description

        super().__init__(title=title, description=description, color=embed_properties.value.color)

        for name, value in embed_properties.value.fields.items():
            self.add_field(name=name.format(server_name=server_name, server=server), value=value.format(server_name=server_name, server=server))

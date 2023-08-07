from __future__ import annotations

from typing import TYPE_CHECKING

from discord.app_commands import AppCommandError

if TYPE_CHECKING:
    from .minecraft_server import MinecraftServer


class MinecraftServerManagerError(AppCommandError):
    pass


class InvalidServerName(MinecraftServerManagerError):
    def __init__(self, server_name: str) -> None:
        self.server_name = server_name
        super().__init__(f"The specified server name `{server_name}` is invalid.")


class ServerProcessingPreviousCommand(MinecraftServerManagerError):
    def __init__(self, server: MinecraftServer) -> None:
        self.server = server
        super().__init__(f"The specified server `{server.name}` is currently processing a previous command.")


class ServerAlreadyRunning(MinecraftServerManagerError):
    def __init__(self, server: MinecraftServer) -> None:
        self.server = server
        super().__init__(f"The specified server `{server.name}` is already running.")


class ServerNotRunning(MinecraftServerManagerError):
    def __init__(self, server: MinecraftServer) -> None:
        self.server = server
        super().__init__(f"The specified server `{server.name}` is not running.")


class MinecraftServerError(AppCommandError):
    pass


class ServerStartFailed(MinecraftServerError):
    def __init__(self, server: MinecraftServer) -> None:
        self.server = server
        super().__init__(f"Failed to start server `{server.name}`.")

class ServerStartTimedOut(MinecraftServerError):
    def __init__(self, server: MinecraftServer) -> None:
        self.server = server
        super().__init__(f"Starting server `{server.name}` timed out.")

from __future__ import annotations

from discord.app_commands import AppCommandError


class ProcessingPreviousCommand(AppCommandError):
    def __init__(self) -> None:
        super().__init__("Another command is still being processed.")

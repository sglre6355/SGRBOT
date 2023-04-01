from __future__ import annotations

from typing import TYPE_CHECKING

from .minecraft_server_manager import MinecraftServerManager

if TYPE_CHECKING:
    from ...bot import SGRBOT


async def setup(bot: SGRBOT) -> None:
    await bot.add_cog(MinecraftServerManager(bot))

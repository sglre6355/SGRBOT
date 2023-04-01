from __future__ import annotations

from typing import TYPE_CHECKING

from .moderator import Moderator

if TYPE_CHECKING:
    from ...bot import SGRBOT


async def setup(bot: SGRBOT) -> None:
    await bot.add_cog(Moderator(bot))

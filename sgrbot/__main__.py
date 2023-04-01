from __future__ import annotations

import os

from dotenv import load_dotenv

from .bot import SGRBOT

if __name__ == '__main__':
    load_dotenv()
    token = os.getenv("BOT_TOKEN")
    bot = SGRBOT()
    bot.run(token)

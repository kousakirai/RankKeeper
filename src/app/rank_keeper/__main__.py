import asyncio
from dotenv import load_dotenv
from rank_keeper.core.core import RankKeeperCore
import os
import discord


bot = RankKeeperCore(
    token=os.environ['BOT_TOKEN'],
    prefix=None,
    intents=discord.Intents.all()
)

async def main():
    await bot.run()

asyncio.run(main())
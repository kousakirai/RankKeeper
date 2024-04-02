import asyncio
from dotenv import load_dotenv
from rank_keeper.core.core import RKCore
import os
import discord
from logging import basicConfig, INFO

basicConfig(level=INFO)

bot = RKCore(
    token=os.environ['BOT_TOKEN'],
    prefix='-',
    intents=discord.Intents.all()
)

async def main():
    await bot.run()

asyncio.run(main())
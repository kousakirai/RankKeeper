from funcs.api import Rank
import asyncio
from dotenv import load_dotenv

load_dotenv()

async def main():
    await Rank('kousakirai', 'steam').get_rank()


asyncio.run(main())
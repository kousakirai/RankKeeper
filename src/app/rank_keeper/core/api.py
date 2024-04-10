import aiohttp
import os


class Rank:
    def __init__(self, name, platform):
        self.name = name
        self.platform = platform
        self.rank = None

        self.fetch_rank()

    async def fetch_rank(self):
        async with aiohttp.ClientSession() as session:
            header = {
                "TRN-Api-Key": os.environ["API_KEY"],
            }
            async with session.get(
                f"https://public-api.tracker.gg/v2/apex/standard/profile/{self.platform}/{self.name}/rank",
                headers=header,
            ) as response:
                data = await response.json()

                self.rank = data["segments"]["level"]["rank"]

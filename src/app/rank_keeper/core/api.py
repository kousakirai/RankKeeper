import aiohttp


class Rank:
    def __init__(self, name, platform):
        self.name = name
        self.platform = platform
        self.rank = None

        self.fetch_rank()

    async def fetch_rank(self):
        async with aiohttp.ClientSession() as session:
            async with session.get(
                f"https://api.tracer.gg/v1/players/{self.platform}/{self.name}/rank"
            ) as response:
                data = await response.json()

                self.rank = data["rank"]

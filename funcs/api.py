import aiohttp
import os
import json
import pprint


class Rank:
    def __init__(self, name, platform):
        self.API_KEY = os.environ.get("API_KEY")
        base_url = "https://public-api.tracker.gg/v2/apex/standard/profile/"
        self.name = name
        self.platform = platform
        self.url = f"{base_url}/{platform}/{name}"
        self.headers = {
            "TRN-Api-Key": str(self.API_KEY)
            }

    async def _fetch(self, session, url):
        async with session.get(url, headers=self.headers) as response:
            return await response.json()
    async def get_rank(self):
        print(self.API_KEY)
        async with aiohttp.ClientSession() as session:
            data = await self._fetch(session, self.url)
            print(data)
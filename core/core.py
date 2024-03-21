from discord.ext import commands


class RankKeeperCore(commands.Bot):
    def init(self, token):
        self.token = token

    async def setup_hook(self):
        self.tree.sync()
        print('CommandTree Setup Complete.')

    async def on_ready(self):
        print(f"{self.name}is booted.")

    async def run(self):
        try:
            await self.start(self.token)
        except:
            print("Failed to Boot.")

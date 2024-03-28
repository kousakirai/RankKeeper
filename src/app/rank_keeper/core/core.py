from discord.ext import commands
import traceback
import discord
from rank_keeper.models.user import User


class RankKeeperCore(commands.Bot):
    def __init__(self, token, prefix, intents):
        super().__init__(
            command_prefix=prefix,
            intents=intents
        )
        self.token = token

    async def setup_hook(self):
        await self._load_cogs()
        await self.tree.sync()
        print('CommandTree Setup Complete.')

    async def _load_cogs(self):
        EXTENSIONS = ['cogs.dynamic_vc', 'cogs.keeper', 'cogs.tts']
        for extension in EXTENSIONS:
            try:
                await self.load_extension('rank_keeper.'+extension)
            except Exception as e:
                traceback.print_exc()
                print(f'Failed to load extension {extension}')
                print(f'Error: {e}')
            else:
                print(f'Successfully loaded extension {extension}')
        await self.load_extension('jishaku')
        self.tree.copy_global_to(guild=discord.Object(993502805409153204))
        print('All cogs were loaded.')

    async def on_ready(self):
        print(f"{self.name}is online.")

    async def run(self):
        try:
            await self.start(self.token)
        except KeyboardInterrupt:
            print("Shutdown....")
            await self.close()

        except discord.LoginFailure:
            print("BOT_TOKEN is invalid.")

        else:
            traceback.print_exc()

from discord.ext import commands
from discord import app_commands, Interaction
from rank_keeper.core.core import RKCore


class Development(commands.GroupCog, name="開発"):
    def __init__(self, bot: RKCore):
        self.bot = bot
        super().__init__()

    @app_commands.command(name='reload', description='Cogを再読み込みします。')
    async def reload_cog(self, inter: Interaction , extension: str):
        await self.bot.reload_extension(extension)
        await inter.response.send_message(f'{extension} reloaded.', ephemeral=True)


async def setup(bot):
    await bot.add_cog(Development(bot))

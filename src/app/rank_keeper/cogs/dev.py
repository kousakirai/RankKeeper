from discord.ext import commands
from discord import app_commands, Interaction
from rank_keeper.core.core import RKCore


class Development(commands.GroupCog, name="dev"):
    def __init__(self, bot: RKCore):
        self.bot = bot
        super().__init__()

    @app_commands.command(name='load', description='Cogをロードします。')
    async def load_cog(self, inter: Interaction , extension: str):
        await self.bot.load_extension(extension)
        await self.bot.tree.sync()
        await inter.response.send_message(f'{extension} loaded.', ephemeral=True)

    @app_commands.command(name='unload', description='Cogをアンロードします。')
    async def unload_cog(self, inter: Interaction , extension: str):
        await self.bot.unload_extension(extension)
        await self.bot.tree.sync()
        await inter.response.send_message(f'{extension} unloaded.', ephemeral=True)

    @app_commands.command(name='reload', description='Cogをリロードします。')
    async def reload_cog(self, inter: Interaction , extension: str):
        await self.bot.reload_extension(extension)
        await self.bot.tree.sync()
        await inter.response.send_message(f'{extension} reloaded.', ephemeral=True)


async def setup(bot):
    await bot.add_cog(Development(bot))

from discord.ext import commands
from discord import app_commands, Interaction
from rank_keeper.core.core import RKCore
import glob


class Development(commands.GroupCog, name="dev"):
    def __init__(self, bot: RKCore):
        self.bot = bot
        super().__init__()

    async def auto_complete_cog(self, inter: Interaction, current: str):
        cog_files = glob.glob('rank_keeper/cogs/*.py')
        return [app_commands.Choice(name=path, value=path) for path in cog_files if path.lower() in current.lower()]

    @app_commands.command(name="load", description="Cogをロードします。")
    @app_commands.autocomplete(extension=auto_complete_cog)
    async def load_cog(self, inter: Interaction, extension: str):
        try:
            await self.bot.load_extension(extension)
        except commands.ExtensionAlreadyLoaded:
            return await inter.response.send_message(f'{extension}は既に読み込まれています。')
        await self.bot.tree.sync()
        await inter.response.send_message(
            f"{extension} loaded.", ephemeral=True
        )

    @app_commands.command(name="unload", description="Cogをアンロードします。")
    @app_commands.autocomplete(extension=auto_complete_cog)
    async def unload_cog(self, inter: Interaction, extension: str):
        try:
            await self.bot.unload_extension(extension)
        except commands.ExtensionNotLoaded:
            return await inter.response.send_message(f'{extension}は読み込まれていません。')
        await self.bot.tree.sync()
        await inter.response.send_message(
            f"{extension} unloaded.", ephemeral=True
        )

    @app_commands.command(name="reload", description="Cogをリロードします。")
    @app_commands.autocomplete(extension=auto_complete_cog)
    async def reload_cog(self, inter: Interaction, extension: str):
        try:
            await self.bot.reload_extension(extension)
        except commands.ExtensionNotLoaded:
            return await inter.response.send_message(f'{extension}は読み込まれていません。')
        await self.bot.tree.sync()
        await inter.response.send_message(
            f"{extension} reloaded.", ephemeral=True
        )


async def setup(bot):
    await bot.add_cog(Development(bot))

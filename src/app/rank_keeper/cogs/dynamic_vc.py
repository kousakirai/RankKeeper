from discord.ext import commands
from discord import (
    ui,
    app_commands,
    ButtonStyle,
    Interaction,
    Member,
    VoiceState,
    VoiceChannel
)
import aiosqlite


class SetupView(ui.View):
    def __init__(self):
        self().__init__(timeout=None)

    @ui.select(cls=ui.ChannelSelect, channel_types=VoiceChannel, placefolder='起点となるボイスチャンネルを選択', max_values=1, min_values=1)
    async def select_channel(self, inter: Interaction, channel: VoiceChannel):
        pass



class DynamicVC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot


    @app_commands.command()
    async def setup(self, inter: Interaction):
        async with aiosqlite.connect('data/temp_vc.db') as conn:
            async with conn.cursor() as cursor:
                await cursor.execute("CREATE TABLE OF MPT EXISTS users (id INTEGER PRIMARY KEY )")


async def setup(bot):
    await bot.add_cog(DynamicVC(bot))

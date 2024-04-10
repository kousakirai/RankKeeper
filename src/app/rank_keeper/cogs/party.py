from discord.ext import commands
from discord import ui, ButtonStyle


class PartyView(ui.View):
    def __init__(self):
        super().__init__(timeout=None)

    @ui.button(label='募集開始', custom_id='party_start', style=ButtonStyle.green)


class PartyCog(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

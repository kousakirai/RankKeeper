from discord.ext import commands
from discord import ui, Interaction, app_commands, ButtonStyle


class AcceptView(ui.View):
    def __init__(self, timeout=180):
        super().__init__(timeout=timeout)

    @ui.button(label="ルールに同意", style=ButtonStyle.green)
    async def accept(self, inter: Interaction, button: ui.Button):
        role = inter.guild.get_role(1222784373762424912)
        await inter.user.add_roles(role)


class RolePanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    async def set_panel(self, inter: Interaction):
        await inter.response.send_message(view=AcceptView(timeout=180))


async def setup(bot):
    await bot.add_cog(RolePanel(bot))
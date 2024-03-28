from discord.ext import commands
from discord import ui, app_commands, SelectOption, Role, Interaction, Colour, Embed, Message, ChannelType
from typing import Dict
from rank_keeper.models.panel import Panel


class RoleSelect(ui.Select):
    def __init__(self, roles:Dict[Role, str]):
        option = []
        for role, emoji in roles.items():
            option.append(SelectOption(label=role.name, value=str(role.id), emoji=emoji))

        super().__init__(
            placeholder="追加したいロール",
            options=option
        )


class RoleView(ui.View):
    def __init__(self, roles):
        super().__init__(timeout=None)
        self.add_item(RoleSelect(roles))

class RolePanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.selected_panel = {}

    @app_commands.command(name="パネルを作成")
    async def create_panel(
        self,
        inter:Interaction,
        title:str,
        color:Colour | int,
        role1:Role=None, emoji1:str=None,
        role2:Role=None, emoji2:str=None,
        role3:Role=None, emoji3:str=None,
        role4:Role=None, emoji4:str=None,
        role5:Role=None, emoji5:str=None,
        role6:Role=None, emoji6:str=None,
        role7:Role=None, emoji7:str=None
    ):
        description = ''
        roles = {role1: emoji1, role2: emoji2, role3: emoji3, role4: emoji4, role5: emoji5, role6: emoji6, role7: emoji7}
        for role, emoji in roles.items():
            description += f"{emoji}: {role}\n"

        embed = Embed(title=title, description=description, color=color)
        message = await inter.channel.send(embed=embed, view=RoleView(roles))
        await Panel.create(message_id=message.id, role_list=roles, description=description)
        await inter.response.send_message(f"パネルを作成しました", ephemeral=True)

    @app_commands.context_menu(name="パネルを選択")
    async def choice_panel(self, inter:Interaction, message: Message):
        if message.author.id != self.bot.user.id:
            return await inter.response.send_message(f"パネルではありません。", ephemeral=True)
        elif message.channel.type != ChannelType.text:
            return
        self.selected_panel[message.channel.id] = message.id
        await inter.response.send_message(f"パネルを選択しました", ephemeral=True)

    @app_commands.command(name="パネルを削除")
    async def delete_panel(self, inter:Interaction):
        message_id = self.selected_panel.pop(inter.channel.id)
        message = await inter.channel.fetch_message(message_id)
        if not message:
            await inter.response.send_message(f"パネルが見つかりませんでした")
        elif message.author.id != self.bot.user.id:
            return await inter.response.send_message(f"パネルではありません。", ephemeral=True)
        elif message.channel.type != ChannelType.text:
            return
        else:
            await Panel(message_id).delete()
            await inter.response.send_message(f"パネルを削除しました", ephemeral=True)

    @app_commands.command(name='ロールを追加')
    async def add_role(self, inter:Interaction, role:Role, emoji:str=None):
        panel = await Panel(self.selected_panel[inter.guild.id]).get()
        if not panel:
            return await inter.response.send_message(f"パネルが見つかりませんでした", ephemeral=True)
        else:
            panel.description += f"{emoji}: {role.name}\n"
            panel.role_list[role] = emoji
            await Panel(self.selected_panel[inter.guild.id]).set(description=panel.description, role_list=panel.role_list)
            await inter.response.send_message(f"ロールを追加しました", ephemeral=True)


async def setup(bot):
    await bot.add_cog(RolePanel(bot))
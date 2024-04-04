from discord.ext import commands
from discord import ui, Interaction, app_commands, ButtonStyle, Role, Embed, Message, SelectOption, utils
from rank_keeper.core.core import RKCore # type: ignore
import aiofiles
import json


class AddRoleSelect(ui.Select):
    def __init__(self, roles: list[Role]):
        options = []
        for role in roles:
            options.append(SelectOption(label=role.name, value=role.id, description=role.mention))
        super().__init__(
            placeholder='追加するロールを選択',
            options=options,
            min_values=1,
            max_values=1
        )

    async def callback(self, inter: Interaction):
        exist_role: str = ''
        added_role: str = ''
        for value in self.values:
            if int(value) in [r.id for r in inter.user.roles]:
                exist_role += f'<@&{int(value)}>\t'
            else:
                await inter.user.add_roles(inter.guild.get_role(int(value)))
                added_role += f'<@&{int(value)}>\t'
        print(exist_role, added_role)
        if exist_role is True and added_role is False:
            await inter.response.send_message(f'{exist_role}は既に付与されています。', ephemeral=True)

        elif exist_role is True and added_role is True:
            await inter.response.send_message(f'{exist_role}は既に付与されていますが、{added_role}は付与しました。', ephemeral=True)

        elif exist_role is False and added_role is True:
            await inter.response.send_message(f'{added_role}を付与しました。', ephemeral=True)

        elif exist_role is False and added_role is False:
            await inter.response.send_message(f'ロールを選択してください。', ephemeral=True)


class RemoveRoleSelect(ui.Select):
    def __init__(self, roles: list[Role]):
        options = []
        for role in roles:
            options.append(SelectOption(label=role, value=role.id, description=role.mention))
        super().__init__(
            placeholder='削除するロールを選択',
            options=options,
            min_values=1,
            max_values=1
        )

    async def callback(self, inter: Interaction):
        not_exist_role: str = ''
        removed_role: str = ''
        for value in self.values:
            if int(value) in [r.id for r in inter.user.roles]:
                await inter.user.remove_roles(inter.guild.get_role(int(value)))
                remove_role += f'<@&{int(value)}>\t'

            else:
                not_exist_role += f'<@&{int(value)}>\t'

        if not_exist_role is True and removed_role is False:
            await inter.response.send_message(f'{not_exist_role}は付与されていませんでした。', ephemeral=True)

        elif not_exist_role is True and removed_role is True:
            await inter.response.send_message(f'{not_exist_role}は付与されていませんでしたが、{removed_role}は解除しました。', ephemeral=True)

        elif not_exist_role is False and removed_role is True:
            await inter.response.send_message(f'{removed_role}を解除しました。', ephemeral=True)

class AcceptView(ui.View):
    def __init__(self, timeout=180):
        super().__init__(timeout=timeout)

    @ui.button(label="ルールに同意", style=ButtonStyle.green, custom_id='accept')
    async def accept(self, inter: Interaction, button: ui.Button):
        role = inter.guild.get_role(1222784373762424912)
        await inter.user.add_roles(role)
        await inter.response.send_message(f'<@&{role.id}>を付与しました。', ephemeral=True)

class RolePanelView(ui.View):
    def __init__(self, timeout, roles: list[Role]= None):
        super().__init__(timeout=timeout)
        self.roles = roles

    @ui.button(label="ロールを追加", style=ButtonStyle.green, custom_id='add_role')
    async def add_role(self, inter: Interaction, button: ui.Button):
        await inter.response.send_message(view=AddRoleView(self.roles), ephemeral=True)

    @ui.button(label="ロールを削除", style=ButtonStyle.red, custom_id='remove_role')
    async def remove_role(self, inter: Interaction, button: ui.Button):
        await inter.response.send_message(view=RemoveRoleView(self.roles), ephemeral=True)

    @ui.button(label='ロールの確認', style=ButtonStyle.primary, custom_id='check_role')
    async def check_role(self, inter: Interaction, button: ui.Button):
        # ロールパネルに登録されているロールのうち、どのロールが付与されているか確認する
        exist_role = []
        for value in self.roles:
            if value.id in [r.id for r in inter.user.roles]:
                exist_role.append(f'<@&{value.id}>\t')
        if len(exist_role) == 0:
            await inter.response.send_message(f'ロールは付与されていません。', ephemeral=True)
        else:
            await inter.response.send_message('付与されているロールは'+ ''.join(exist_role) + 'です。', ephemeral=True)


class AddRoleView(ui.View):
    def __init__(self, roles: list[Role]= None):
        super().__init__(timeout=None)
        self.add_item(AddRoleSelect(roles))


class RemoveRoleView(ui.View):
    def __init__(self, roles: list[Role]):
        super().__init__(timeout=None)
        self.add_item(RemoveRoleSelect(roles))


class AcceptPanel(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @app_commands.command()
    async def set_panel(self, inter: Interaction):
        await inter.response.send_message(view=AcceptView(timeout=None))


class RolePanel(commands.Cog):
    def __init__(self, bot: RKCore):
        self.bot = bot
        self.ctx_menu = app_commands.ContextMenu(
            name='パネル選択',
            callback=self.select_panel
        )
        self.bot.tree.add_command(self.ctx_menu)
        self.selected_panel: dict[id, Message] = {}

    @app_commands.command()
    @app_commands.describe(title='タイトル',role='パネルに設定するロール',)
    async def setup_panel(self, inter: Interaction, title:str, role: Role):
        embed = Embed(title=title, description='\n'.join([f'<@&{role.id}>']))
        view = RolePanelView(timeout=None, roles=[role])
        message = await inter.channel.send(embed=embed, view=view)
        await inter.response.send_message(f'パネルを作成しました。', ephemeral=True)
        self.selected_panel[message.guild.id] = message
        async with aiofiles.open('rank_keeper/data/panel.json', 'w+') as f:
            data = await f.read()
            if not data:
                data = {}

            if message.guild.id not in data:
                data[message.guild.id] = {}

            data[message.guild.id][message.id] = [role.id]
            await f.write(json.dumps(data))

    async def select_panel(self, inter: Interaction, message: Message):
        async with aiofiles.open('rank_keeper/data/panel.json', 'r') as f:
            data = json.loads(await f.read())
        if str(message.id) in data.get(str(inter.guild.id)):
            self.selected_panel[message.guild.id] = message
            await inter.response.send_message('パネルを選択しました。', ephemeral=True)
        else:
            await inter.response.send_message('このメッセージはパネルではありません。', ephemeral=True)

    @app_commands.command(name='add_role')
    async def add_role_to_panel(self, inter: Interaction, role_name: str):
        message = self.selected_panel.get(inter.guild.id)
        role_id = int(role_name.replace('<@&', '').replace('>', ''))
        async with aiofiles.open('rank_keeper/data/panel.json', 'r') as f:
            data = json.loads(await f.read(),parse_int=int)
            if message is None:
                return await inter.response.send_message('パネルを選択してください。', ephemeral=True)

            elif role_id in data[str(inter.guild.id)][str(message.id)]:
                return await inter.response.send_message(f'{role_name}は既に追加されています。', ephemeral=True)

        async with aiofiles.open('rank_keeper/data/panel.json', 'r') as f:
            data = json.loads(await f.read())
            data[str(inter.guild.id)][str(message.id)].append(role_id)

        async with aiofiles.open('rank_keeper/data/panel.json', 'w') as f:
            await f.write(json.dumps(data, indent=4))

        view = RolePanelView(timeout=None, roles=data)
        embed = Embed(title=message.embeds[0].title, description=message.embeds[0].description+f'\n<@&{role_id}>')
        await self.selected_panel[inter.guild.id].edit(embed=embed, view=view)
        await inter.response.send_message(f'{role_name}を追加しました。', ephemeral=True)

    @app_commands.command(name='remove_role')
    async def remove_role_to_panel(self, inter: Interaction, role_name: str):
        message = self.selected_panel.get(inter.guild.id)
        role_id = int(role_name.replace('<@&', '').replace('>', ''))
        if message is None:
            return await inter.response.send_message('パネルを選択してください。', ephemeral=True)

        async with aiofiles.open('rank_keeper/data/panel.json', 'r') as f:
            data = json.loads(await f.read())
            data[str(inter.guild.id)][str(message.id)].remove(role_id)
        async with aiofiles.open('rank_keeper/data/panel.json', 'w+') as f:
            await f.write(json.dumps(data, indent=4))

        view = RolePanelView(timeout=None, roles=data)
        await self.selected_panel[inter.guild.id].edit(view=view)


async def setup(bot: RKCore):
    await bot.add_cog(AcceptPanel(bot))
    await bot.add_cog(RolePanel(bot))
    bot.add_view(AcceptView(timeout=None))
    bot.add_view(RolePanelView(timeout=None))

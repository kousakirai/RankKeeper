from discord.ext import commands
from discord import app_commands, utils
from discord import ui, Interaction
from discord.ext import tasks
from rank_keeper.models.user import User
from rank_keeper.core.api import Rank
import os


class Modal(ui.Modal, title='情報登録'):

    platform = ui.TextInput(label='プラットフォーム', placeholder='PCなら1、PS4なら2,Switchなら3と入力してください。')
    name = ui.TextInput(label='ユーザー名', placeholder='PCの方はEAアカウント名、PS4、Switchならそのままのユーザー名を入力してください。')

    async def on_submit(self, interaction: Interaction) -> None:
        if await User(interaction.user.id).get():
            await User(interaction.user.id).set(
                name=self.name,
                platform=self.platform
            )
            await interaction.response.send_message('情報を更新しました。')
        else:
            await User.create(
                id=interaction.user.id,
                name=self.name,
                platform=self.platform
            )
            await interaction.response.send_message('情報を登録しました。')

class Keeper(commands.Cog):
    def __init__(self, bot):
        self.bot = bot
        self.guild = bot.get_guild(os.environ.get('GUILD_ID'))

    @app_commands.command(name='setup', description='ロール調整機能に必要なコマンドです。必ず実行してください。')
    async def regist_data(self, inter: Interaction):
        await inter.response.send_modal(Modal())

    @tasks.loop(hours=24)
    async def update_rank(self):
        users = await User.get_all()
        for user in users:
            rank = Rank(users.name, users.platform).fetch_rank()
            pass

async def setup(bot):
    await bot.add_cog(Keeper(bot))
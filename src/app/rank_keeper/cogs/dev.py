from discord.ext import commands
from discord import app_commands, Interaction, Embed
from rank_keeper.core.core import RKCore
import glob
import asyncio


class Development(commands.GroupCog, name="dev"):
    def __init__(self, bot: RKCore):
        self.bot = bot
        super().__init__()

    async def auto_complete_cog(self, inter: Interaction, current: str):
        cog_files = glob.glob("rank_keeper/cogs/*.py")
        return [
            app_commands.Choice(name=path, value=path)
            for path in cog_files
            if current.lower() in path.lower()
        ]

    @app_commands.command(name="load", description="Cogをロードします。")
    @app_commands.autocomplete(extension=auto_complete_cog)
    async def load_cog(self, inter: Interaction, extension: str):
        try:
            await self.bot.load_extension(extension)
        except commands.ExtensionAlreadyLoaded:
            return await inter.response.send_message(
                f"{extension}は既に読み込まれています。"
            )
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
            return await inter.response.send_message(
                f"{extension}は読み込まれていません。"
            )
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
            return await inter.response.send_message(
                f"{extension}は読み込まれていません。"
            )
        await self.bot.tree.sync()
        await inter.response.send_message(
            f"{extension} reloaded.", ephemeral=True
        )

    @app_commands.command(name="rank_reset", description="スプリット(またはシーズン)切り替わり時にランクをリセット。※運営のみ")
    @app_commands.checks.has_permissions(moderate_members=True)
    async def rank_reset(self, inter: Interaction):
        await inter.response.defer()
        rank_roles = {
            'rookie': 1094479147922894928,
            'bronze': 839139993704202314,
            'silver': 839139991526834222,
            'gold': 839139996799598612,
            'platinum': 839139988616642590,
            'diamond': 839139985742626816,
            'master': 839139982437777440,
            'predator': 839140002088484914
        }
        members = inter.guild.members
        for member in members:
            if member.bot:
                continue

            role_ids = [role.id for role in member.roles]
            set_roles = set(role_ids)
            nothing_doing_roles = set([int(rank_roles['rookie']), int(rank_roles['bronze'])])
            become_bronze_roles = set([int(rank_roles['silver']), int(rank_roles['gold']), int(rank_roles['platinum'])])
            become_silver_roles = set([int(rank_roles['diamond'])])
            become_gold_roles = set([int(rank_roles['master']), int(rank_roles['predator'])])
            if len(member.roles) == 0:
                continue

            elif not set_roles.isdisjoint(nothing_doing_roles) and len(set_roles.intersection(nothing_doing_roles)) == 1:
                continue

            elif not set_roles.isdisjoint(become_bronze_roles) and len(set_roles.intersection(become_bronze_roles)) == 1:
                await member.remove_roles(*[inter.guild.get_role(role) for role in list(set_roles & become_bronze_roles)])
                await member.add_roles(inter.guild.get_role(rank_roles['bronze']))
                print(f'{member.display_name} was removed silver or gold or platinum roles and added bronze role.')

            elif not set_roles.isdisjoint(become_silver_roles) and len(set_roles.intersection(become_silver_roles)) == 1:
                await member.remove_roles(*[inter.guild.get_role(role) for role in list(set_roles & become_silver_roles)])
                await member.add_roles(inter.guild.get_role(rank_roles['silver']))
                print(f'{member.display_name} was removed diamond role and added silver role.')

            elif not set_roles.isdisjoint(become_gold_roles) and len(set_roles.intersection(become_gold_roles)) == 1:
                await member.remove_roles(*[inter.guild.get_role(role) for role in list(set_roles & become_gold_roles)])
                await member.add_roles(inter.guild.get_role(rank_roles['gold']))
                print(f'{member.display_name} was removed master or predator role and added gold role.')

            else:
                continue
            await asyncio.sleep(1)
        embed = Embed(title='処理完了', description='ランクをリセットしました。')
        await inter.followup.send(embed=embed)

async def setup(bot):
    await bot.add_cog(Development(bot))

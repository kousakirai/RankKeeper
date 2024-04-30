from discord.ext import commands
from discord import app_commands, Interaction, utils, Embed
import random


class RandomShuffler(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    async def category_autocomplete(
        self, inter: Interaction, current: str
    ) -> list[app_commands.Choice[str]]:
        categories = inter.guild.categories
        return [
            app_commands.Choice(name=category.name, value=str(category.id))
            for category in categories
            if current.lower() in category.name.lower()
        ]

    @app_commands.command()
    @app_commands.describe(mode="開催するモードを選んでください。")
    @app_commands.choices(mode=[
        app_commands.Choice(name="トリオ", value="1"),
        app_commands.Choice(name="デュオ", value="2"),
        app_commands.Choice(name="チーデス", value="3"),
        app_commands.Choice(name="コントロール", value="4"),
        app_commands.Choice(name="ガンゲーム", value="5"),
    ])
    @app_commands.autocomplete(category_name=category_autocomplete)
    async def shuffle(
        self,
        inter: Interaction,
        mode: app_commands.Choice[str],
        category_name: str,
    ):
        members = inter.guild.get_member(inter.user.id).voice.channel.members
        category = utils.get(inter.guild.categories, name=category_name)
        all_team_list = []
        if mode.value == '1':
            for i in range(members // 3 + 1):
                channel = await inter.guild.create_voice_channel(name=f'Team - {i+1}', category=category)
                if  1 <= len(member) <= 2:
                    counts = 2
                else:
                    counts = 3
                member_list = f'Team - {i+1} '
                for member in random.sample(members, counts):
                    members.remove(member)
                    member_list += f'{member.mention} '
                    await member.move_to(channel=channel)
                all_team_list.append(member_list)

        if mode.value == '2':
            for i in range(members // 2 + 1):
                channel = await inter.guild.create_voice_channel(name=f'Team - {i+1}', category=category)
                if  1 <= len(member) <= 2:
                    counts = 2
                else:
                    counts = 1
                member_list = f'Team - {i+1} '
                for member in random.sample(members, counts):
                    members.remove(member)
                    member_list += f'{member.mention} '
                    await member.move_to(channel=channel)
                all_team_list.append(member_list)

        if mode.value == '3' or '4' or '5':
            if len(members) < 18 and mode.value == '4':
                return await inter.response.send_message('コントロールモードの最大人数を超過しています。別のモードをお選びください。')

            elif len(members) < 12 and mode.value == '5':
                return await inter.response.send_message('ガンゲームモードの最大人数を超過しています。別のモードをお選びください。')

            for i in range(2):
                channel = await inter.guild.create_voice_channel(name=f'Team - {i+1}', category=category)
                member_list = f'Team - {i+1}'
                if i == 1:
                    for member in member_list:
                        members.remove(member)
                        member_list += f'{member.mention}'
                        await member.move_to(channel=channel)
                else:
                    for member in random.sample(members, (len(members) + 1) // 2):
                        members.remove(member)
                        member_list += f'{member.mention}'
                        await member.move_to(channel=channel)
                all_team_list.append(member_list)

        else:
            pass

        embed = Embed(title='シャッフル完了', description=f'ゲームモード:{mode.name}' + '\n'.join(all_team_list))
        await inter.response.send_message(embed)


async def setup(bot):
    await bot.add_cog(RandomShuffler(bot))

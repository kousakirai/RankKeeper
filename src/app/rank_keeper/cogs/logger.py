from discord.ext import commands
from rank_keeper.core.core import RKCore
from discord import Member, Invite, Embed, Colour, AllowedMentions
from typing import Union


class EventLoggerCog(commands.Cog):
    def __init__(self, bot: RKCore):
        self.bot = bot

    def get_invite_code(self, before_invite_list, after_invite_list) -> Union[Invite, None]:
        before_code_list = [invite.code for invite in before_invite_list]
        after_code_list = [invite.code for invite in after_invite_list]
        for before_code in before_code_list:
            for after_code in after_code_list:
                if before_code.uses < after_code.uses:
                    return after_code

    @commands.Cog.listener()
    async def  on_member_join(self, member: Member) -> None:
        code = self.get_invite_code(self.bot.invites, member.guild.invites)
        log_embed = Embed(title='参加通知', description=' ', colour=Colour.green)
        log_embed.add_field(name=f'参加日時: <t:{member.joined_at.timestamp()}:f>', value='', inline=False)
        log_embed.add_field(name=f'招待コード: {code}',value=' ', inline=False)
        log_embed.set_author(name=member.name, icon_url=member.display_icon)
        await self.bot.log_channel.send(embed=log_embed)
        await member.guild.system_channel.send(f'{member.mention}が参加しました。', allowed_mentions=AllowedMentions(everyone=False, users=False, roles=False, replied_user=False))

    @commands.Cog.listener()
    async def on_member_leave(self, member: Member) -> None:
        log_embed = Embed(title='退室通知', description=' ', colour=Colour.red)
        log_embed.add_field(name='ロール:`{、}`'.format([role.name for role in member.roles]), value=' ', inline=False)
        log_embed.add_field(name=f'現在のメンバー数:{len(member.guild.members)}', value=' ', inline=False)
        await self.bot.log_channel.send(embed=log_embed)
        await member.guild.system_channel.send(f'{member.mention}が退出しました。', allowed_mentions=AllowedMentions(everyone=False, users=False, roles=False, replied_user=False))

    @commands.Cog.listener()
    async def on_member_update(self, before: Member, after: Member) -> None:
        log_embed = Embed(title='ロール更新', description=' ', colour=Colour.yellow)
        log_embed.add_field(name='更新前のロール：`{、}`'.format([role.name for role in before.roles]), value='', inline=False)
        log_embed.add_field(name='更新後のロール：`{、}`'.format([role.name for role in after.roles]), value='', inline=False)
        await self.bot.log_channel.send(embed=log_embed)


async def setup(bot):
    await bot.add_cog(EventLoggerCog(bot))
from discord.ext import commands
from discord import ui, app_commands, ButtonStyle, Interaction, Member, VoiceState


class CasualEntryView(ui.View):
    def __init__(self):
        super().__init__()

    @ui.button(label='募集を開始する', style=ButtonStyle.green, row=4)
    async def start_button(self, interaction: Interaction, button: ui.Button):
        channel = self.bot.get_channel()
        await interaction.response.send_message(
            content=f'募集を開始しました。',
            ephemeral=True
        )


class RankMatchEntryView(ui.View):
    pass


class DynamicVC(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_voice_state_update(self, member: Member, before: VoiceState, after: VoiceState):
        # ユーザーがボイスチャンネルに参加した場合
        if after.channel is not None:
            if after.channel.category == '👪-カジュアル・その他のモード':
                # 一時的なボイスチャンネルを作成
                category = after.channel.category
                temp_channel = await category.create_voice_channel(f'Temporary Channel for {member.display_name}')
                await member.move_to(temp_channel)

        # ユーザーがボイスチャンネルから退出した場合
        elif not before.channel == after.channel:
            # 一時的なボイスチャンネルを削除
            if before.channel.name.startswith('Temporary Channel for') and len(before.channel.members) == 0:
                await before.channel.delete()

async def setup(bot):
    await bot.add_cog(DynamicVC(bot))
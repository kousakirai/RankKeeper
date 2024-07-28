from discord.ext import commands, tasks
from discord import Message, Embed, Colour
from rank_keeper.models.bump import Bump
import time
from datetime import datetime, timedelta
from zoneinfo import ZoneInfo
from rank_keeper.core.core import RKCore


DISBOARD_ID = 302050872383242240


class BumpCog(commands.GroupCog, name="bump"):
    def __init__(self, bot: RKCore):
        self.bot = bot
        self.channel_id = 1219247231224385591
        self.role_id = 1219929722901893132
        self.guild_id = 811206817942208514
        self.check_bump.start()

    @commands.Cog.listener(name="on_message")
    async def on_message_bump(self, message: Message):
        now_time = datetime.now(tz=ZoneInfo("Asia/Tokyo"))
        two_hours_ago = now_time + timedelta(hours=2)
        bump = await Bump(message.channel.id).get()
        if not bump:
            return
        if message.author.id == DISBOARD_ID:
            try:
                if "disboard.org/images/bot-command-image-bump.png" in str(
                    message.embeds[0].image.url
                ):
                    await Bump(message.channel.id).set(bump_time=time.time())
                    embed = Embed(
                        title="BUMPを検知しました。",
                        description="",
                        colour=Colour.blue(),
                    )
                    embed.add_field(
                        name=f"<t:{two_hours_ago.timestamp()}:f>に通知します。"
                    )
                    await message.channel.send(embed=embed)

            except IndexError:
                pass

    @tasks.loop(seconds=10)
    async def check_bump(self):
        bump = await Bump(self.channel_id).get()
        try:
            if time.time() > bump.bump_time:
                await Bump(self.channel_id).set(bump_time=None)
                channel = await self.bot.get_guild(self.guild_id).get_channel(
                    self.channel_id
                )
                embed = Embed(
                    title="Bumpの時間です！",
                    description="",
                    colour=Colour.blue(),
                )
                embed.add_filed(name="`/bump`で表示順をアップします。")
                await channel.send(f"<@&{self.role_id}>", embed=embed)
        except AttributeError:
            pass


async def setup(bot):
    await bot.add_cog(BumpCog(bot))

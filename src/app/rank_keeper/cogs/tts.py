from discord.ext import commands
import discord
from rank_keeper.core.voicevox import VoiceGenerator
from rank_keeper.models.user import User


class TextToSpeech(commands.Cog):
    def __init__(self, bot):
        self.bot = bot

    @commands.Cog.listener()
    async def on_message(self, message: discord.Message):
        # 発言があったチャンネルがボイスチャンネルでなければ無視
        if message.channel.type != discord.ChannelType.voice:
            return

        # 発言者がボイスチャンネルにいなければ無視
        elif message.author.voice is None:
            return

        else:
            #VoiceGeneratorを利用して音声を生成
            voice_generator = VoiceGenerator('http://localhost:50021')
            voice_generator.generate_voice(message.content)

async def setup(bot):
    await bot.add_cog(TextToSpeech(bot))
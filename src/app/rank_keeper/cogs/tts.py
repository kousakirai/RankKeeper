from discord.ext import commands
from discord import app_commands, Interaction, VoiceChannel, VoiceClient, Message, FFmpegAudio
from rank_keeper.core.voicevox import VoiceGenerator
from rank_keeper.models.user import User
from rank_keeper.core.core import RKCore
from typing import Dict
import asyncio
import re


class AudioQueue(asyncio.Queue):
    def __init__(self):
        super().__init__(100)

    def __getitem__(self, idx):
        return self._queue[idx]

    def to_list(self):
        return list(self._queue)

    def reset(self):
        self._queue.clear()


class AudioStatus:
    def __init__(self, vc: VoiceClient):
        self.vc: VoiceClient = vc
        self.queue = AudioQueue()
        self.playing = asyncio.Event()
        asyncio.create_task(self.playing_task())

    async def add_audio(self, voice: bytes):
        await self.queue.put(voice)

    def get_list(self):
        return self.queue.to_list()

    async def playing_task(self):
        while True:
            self.playing.clear()
            voice = await asyncio.wait_for(self.queue.get(), timeout=None)
            self.vc.play(FFmpegAudio(voice), after=self.play_next)
            await self.playing.wait()

    def play_next(self, err=None):
        self.playing.set()

    async def leave(self):
        self.queue.reset()
        if self.vc:
            await self.vc.disconnect()
            self.vc = None


class TextToSpeech(commands.Cog):
    def __init__(self, bot: RKCore):
        self.bot = bot
        self.audio_status: Dict[int, AudioStatus] = {}

    @app_commands.command(name='join', description='BotをVCに参加させます。')
    async def join(self, inter: Interaction):
        if not inter.user.voice or not inter.user.voice.channel:
            return await inter.response.send_message('VCに参加してから実行してください。', ephemeral=True)
        vc = await inter.user.voice.channel.connect()
        self.audio_status[inter.user.voice.channel.id] = AudioStatus(vc)
        await inter.response.send_message('VCに参加しました。', ephemeral=True)

    @app_commands.command(name='leave', description='BotをVCから退室させます。')
    async def leave(self, inter: Interaction):
        if not inter.user.voice or not inter.user.voice.channel:
            return await inter.response.send_message('VCに参加してから実行してください。', ephemeral=True)
        vc = self.audio_status.pop(inter.user.voice.channel.id, None)
        if vc:
            await vc.disconnect()
        else:
            return await inter.response.send_message('VCに参加していません。', ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        user = await User(message.author.id).get()
        read_msg = message.content
        if message.author.bot:
            return

        elif message.author.voice.channel.id not in self.audio_status:
            return
        # URL置換
        read_msg = re.sub(r"https?://.*?\s|https?://.*?$", "URL", read_msg)

        # ネタバレ置換
        read_msg = re.sub(r"\|\|.*?\|\|", "ネタバレ", read_msg)

        # メンション置換
        if "<@" and ">" in message.content:
            Temp = re.findall("<@!?([0-9]+)>", message.content)
            for i in range(len(Temp)):
                Temp[i] = int(Temp[i])
                _user = message.guild.get_member(Temp[i])
                read_msg = re.sub(f"<@!?{Temp[i]}>", "アット" + _user.display_name, read_msg)

        # サーバー絵文字置換
        read_msg = re.sub(r"<:(.*?):[0-9]+>", r"\1", read_msg)

        # *text*置換
        read_msg = re.sub(r"\*(.*?)\*", r"\1", read_msg)

        # _hoge_置換
        read_msg = re.sub(r"_(.*?)_", r"\1", read_msg)

        if not user:
            user = await User.create(id=message.author.id)
        voice = await self.bot.generator.generate_voice(read_msg, user.speaker)
        await self.audio_status[message.author.voice.channel.id].add_audio(voice)


async def setup(bot):
    await bot.add_cog(TextToSpeech(bot))
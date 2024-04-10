from discord.ext import commands
from discord import (
    app_commands,
    Interaction,
    VoiceClient,
    Message,
    ui,
    SelectOption,
    User,
    ClientUser,
    ClientException,
)
from rank_keeper.core.core import RKCore
from rank_keeper.core.commons import jsonkey_to_int_when_possible
from rank_keeper.core.voicevox import VoiceSource
from typing import Dict
import asyncio
import re
import aiofiles
import json
import aiohttp
from logging import getLogger
import time


LOG = getLogger(__name__)


import collections


def deepupdate(dict_base, other):
    for k, v in other.items():
        if isinstance(v, collections.Mapping) and k in dict_base:
            deepupdate(dict_base[k], v)
        else:
            dict_base[k] = v


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

    async def add_audio(self, voice):
        await self.queue.put(voice)

    def get_list(self):
        return self.queue.to_list()

    async def playing_task(self):
        while True:
            self.playing.clear()
            voice = await asyncio.wait_for(self.queue.get(), timeout=None)
            self.vc.play(voice, after=self.play_next)
            await self.playing.wait()

    def play_next(self, err=None):
        self.playing.set()

    async def leave(self):
        self.queue.reset()
        if self.vc:
            await self.vc.disconnect()
            self.vc = None


class StyleSelect(ui.Select):
    def __init__(self, styles: dict[str, int]):
        options = []
        for style_name, style_id in styles.items():
            options.append(SelectOption(label=style_name, value=style_id))

        super().__init__(
            placeholder="スタイルを選択",
            options=options,
            max_values=1,
            min_values=1,
        )

    async def callback(self, inter: Interaction):
        async with aiofiles.open("rank_keeper/data/tts.join") as f:
            data = json.loads(
                await f.read(), object_pairs_hook=jsonkey_to_int_when_possible
            )
            data[inter.guild.id] = int(self.values[0])
            await f.write(json.dumps(data, indent=4))
        await inter.response.send_message("変更しました。", ephemeral=True)


class SpeakerSelect(ui.Select):
    def __init__(self, speakers: dict):
        options = []
        # speakers = speaker_name: {'speaker_uuid': speaker_uuid, 'styles': styles_list}
        for speaker_name, styles_data in speakers.items():
            options.append(
                SelectOption(
                    label=speaker_name,
                    value=speaker_name,
                    description=styles_data["speaker_uuid"],
                )
            )
        self.speakers = speakers
        super().__init__(
            placeholder="話者を選択",
            options=options,
            max_values=1,
            min_values=1,
        )

    async def callback(self, inter: Interaction):
        for value in self.values:
            styles: dict = self.speakers[value]["styles"]
            view = ui.View(timeout=None)
            view.add_item(StyleSelect(styles))
            await inter.response.send_message(view=view, ephemeral=True)


class TextToSpeech(commands.Cog):
    def __init__(self, bot: RKCore):
        self.bot = bot
        self.audio_status: Dict[int, AudioStatus] = {}

    @app_commands.command(name="join", description="BotをVCに参加させます。")
    async def join(self, inter: Interaction):
        if not inter.user.voice or not inter.user.voice.channel:
            return await inter.response.send_message(
                "VCに参加してから実行してください。", ephemeral=True
            )
        await inter.response.defer()
        while True:
            try:
                vc = await inter.user.voice.channel.connect()
            except ClientException:
                LOG.info(
                    f"Failed to connect to {inter.user.voice.channel}. try reconnect 5 seconds later."
                )
                time.sleep(5)
            finally:
                break

        self.audio_status[inter.user.voice.channel.id] = AudioStatus(vc)
        await inter.followup.send("VCに参加しました。", ephemeral=True)

    @app_commands.command(
        name="leave", description="BotをVCから退室させます。"
    )
    async def leave(self, inter: Interaction):
        if not inter.user.voice or not inter.user.voice.channel:
            return await inter.response.send_message(
                "VCに参加してから実行してください。", ephemeral=True
            )
        await inter.response.defer()
        vc = self.audio_status.pop(inter.user.voice.channel.id, None)
        if vc:
            await vc.leave()
        else:
            return await inter.followup.send_message(
                "VCに参加していません。", ephemeral=True
            )

    @app_commands.command(
        name="change_speaker", description="話者を変更します。"
    )
    async def change_speaker(self, inter: Interaction):
        view = ui.View(timeout=None)
        speakers = {}
        async with aiohttp.ClientSession() as session:
            async with session.get(
                "external://voicevox_engine:50021/speakers"
            ) as res:
                result = await res.json()
        for speaker in result:
            deepupdate(
                speakers,
                {
                    speaker["styles"]["name"]: {
                        "speaker_uuid": speaker["speaker_uuid"],
                        "styles": speaker["styles"],
                    }
                },
            )
        view.add_item(SpeakerSelect(speakers=speakers))
        await inter.response.send_message(view=view, ephemeral=True)

    @commands.Cog.listener()
    async def on_message(self, message: Message):
        if message.author.bot:
            return

        if isinstance(message.author, User) or isinstance(
            message.author, ClientUser
        ):
            message.author = message.guild.get_member(message.author.id)

        read_msg = message.content
        voice_channel = message.author.voice.channel
        voice_status = self.audio_status.get(voice_channel.id, None)

        if voice_status is None:
            return

        async with aiofiles.open("rank_keeper/data/tts.json", "r+") as f:
            # LOG.info(f'raw_data: {await f.read()} json_data: {json.loads(await f.read(), object_hook=jsonkey_to_int_when_possible)}')
            data = json.loads(
                await f.read(), object_pairs_hook=jsonkey_to_int_when_possible
            )
            LOG.info(data)
            if data is None:
                data = {}

            guild_id = message.guild.id
            LOG.info(f"guild_id: {guild_id}")
            deepupdate(data, {guild_id: {"users": {message.author.id: 2}}})
            LOG.info(f"raw_data: {data}")
            await f.write(json.dumps(data, indent=4))

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
                read_msg = re.sub(
                    f"<@!?{Temp[i]}>", "アット" + _user.display_name, read_msg
                )

        # サーバー絵文字置換
        read_msg = re.sub(r"<:(.*?):[0-9]+>", r"\1", read_msg)

        # *text*置換
        read_msg = re.sub(r"\*(.*?)\*", r"\1", read_msg)

        # _hoge_置換
        read_msg = re.sub(r"_(.*?)_", r"\1", read_msg)
        async with aiofiles.open("rank_keeper/data/tts.json", "r") as f:
            data = json.loads(await f.read())
            speaker = data[message.guild.id]["users"][message.author.id]
        LOG.info(f"Replaced text: {read_msg}")
        voice = await VoiceSource.generate_voice(
            url="external://voicevox_engine:50021",
            param={"text": read_msg, "voice": speaker.voice},
        )
        await voice_status.add_audio(voice=voice)


async def setup(bot):
    await bot.add_cog(TextToSpeech(bot))

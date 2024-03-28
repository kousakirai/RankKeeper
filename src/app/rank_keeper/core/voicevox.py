import aiohttp
import asyncio
import discord

class Speaker:
    "Voicevox上で使用可能な話者のクラス。使用可能なスタイルを切替可能。"
    def __init__(self, speaker: str, styles: dict):
        self.speaker: str = speaker
        self.styles: dict = styles
        self.default: dict = {"name": "ノーマル", "id": int(styles[0]["id"])}
        self.used_style: dict = None

    def change_style(self, style: str) -> None:
        if style not in self.styles:
            raise ValueError(f"{style} is not a valid style.")
        self.use_style = style

    def get_used_style(self) -> dict:
        return self.default if self.used_style is None else self.used_style

    def return_valid_style(self) -> dict:
        return self.styles

class VoiceGenerator:
    """
    VoiceGeneratorはVoiceVox Engineを利用して音声を生成するクラス。
    _create_queryで音声合成に必要なクエリを文字列から生成する。
    それをgenerate_voiceに渡すことで音声が生成される。
    """
    def __init__(self, url: str):
        self.base_url = url
        self.valid_speakers: dict = None
        loop = asyncio.get_runnning_loop()
        loop.run_in_executor(None, self._get_speakers)


    async def _get_speakers(self) -> list:
        """
        get_speakersはVoicevox上で使用可能な話者のSpeakerクラスのリストを返す。
        """
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url + "/speakers") as response:
                for speaker in await response.json():
                    self.valid_speakers[speaker["name"]] = Speaker(speaker["name"], speaker["styles"])

    async def get_speakers(self) -> dict:
        if self.valid_speakers is None:
            await self._get_speakers()
        return self.valid_speakers.keys()

    async def _create_query(self, text: str, speaker: Speaker) -> dict:
        params = {
            'text': text,
            'speaker': speaker.get_used_style['id']
        }
        async with aiohttp.ClientSession() as session:
            async with session.get(self.base_url + "/audio_query", params=params) as response:
                return await response.json(), params

    async def generate_voice(self, text: str, speaker: Speaker) -> bytes:
        headers = {"Content-Type": "application/json"}
        data, params = await self._create_query(text, speaker)
        async with aiohttp.ClientSession() as session:
            async with session.post(self.base_url + "/synthesis", json=await self._create_query(text, speaker), headers=headers) as response:
                return discord.FFmpegAudio(await response.read())


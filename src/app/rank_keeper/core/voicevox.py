import aiohttp
import asyncio
import discord
from logging import getLogger
import time
import io


ffmpeg_options = {
    'options': '-vn'
}


class VoiceSource(discord.PCMVolumeTransformer):
    def __init__(self, source, *, volume=0.5):
        super().__init__(source, volume)


    @classmethod
    async def generate_voice(cls, url, params: dict):
        async with aiohttp.ClientSession() as session:
            async with session.get(url+'/audio_query', params=params) as resp:
                query = await resp.json()

            async with session.post(url, params=params, data=query) as resp:
                result = await resp.read()

            filename = 'voice'
            return discord.FFmpegPCMAudio(io.BytesIO(result), **ffmpeg_options)

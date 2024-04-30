import asyncio

from discord import app_commands, PCMVolumeTransformer, FFmpegPCMAudio, VoiceChannel, Interaction, SelectOption, TextChannel, Embed, Colour, File, VoiceClient
from discord.ui import View, Select
import youtube_dl
from googleapiclient.discovery import build

from discord.ext import commands
import os
import io
from typing import Union
import functools

# Suppress noise about console usage from errors
youtube_dl.utils.bug_reports_message = lambda: ''


ytdl_format_options = {
    'format': 'bestaudio/best',
    'outtmpl': '%(extractor)s-%(id)s-%(title)s.%(ext)s',
    'restrictfilenames': True,
    'noplaylist': True,
    'nocheckcertificate': True,
    'ignoreerrors': False,
    'logtostderr': False,
    'quiet': True,
    'no_warnings': True,
    'default_search': 'auto',
    'source_address': '0.0.0.0',# bind to ipv4 since ipv6 addresses cause issues sometimes
    'write_thumbnail': True
}

ffmpeg_options = {
    'options': '-vn',
}

ytdl = youtube_dl.YoutubeDL(ytdl_format_options)
youtube = build(
    'youtube',
    'v3',
    developerKey=os.environ.get('YOUTUBE_API_KEY')
)


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
    def __init__(self, inter: Interaction, channel: Union[VoiceChannel, TextChannel], vc: VoiceClient):
        self.vc: VoiceClient = vc
        self.inter: Interaction = inter
        self.queue = AudioQueue()
        self.playing = asyncio.Event()
        asyncio.create_task(self.playing_task())

    async def add_audio(self, source):
        await self.queue.put(source)

    def get_list(self):
        return self.queue.to_list()

    async def playing_task(self):
        while True:
            self.playing.clear()
            try:
                source = await asyncio.wait_for(self.queue.get(), timeout=180)
            except asyncio.TimeoutError:
                asyncio.create_task(self.leave())
            self.vc.play(source, after=self.play_next)
            await self.playing.wait()

    def play_next(self, err=None):
        self.playing.set()

    async def leave(self):
        self.queue.reset()
        if self.vc:
            await self.vc.disconnect()
            self.vc = None

    @property
    def is_playing(self):
        return self.vc.is_playing()

    def stop(self):
        self.queue.reset()
        self.vc.stop()

    def pause(self):
        '''再生を一時的に停止する。また、queueの中身は保持する。'''
        self.vc.pause()

    def resume(self):
        self.vc.resume()

    def skip(self):
        '''次の曲の再生に移る'''
        self.vc.stop()


audio_statuses: dict[int, AudioStatus] = {}


class SearchView(View):
    def __init__(self, data_list: list, channel: Union[TextChannel, VoiceChannel]):
        self.data = data_list
        super().__init__(timeout=None)
        self.add_item(SearchSelect(data_list, channel))


class SearchSelect(Select):
    def __init__(self, data_list: list, channel: Union[TextChannel, VoiceChannel]):
        options = []
        self.channel = channel
        for data in data_list:
            options.append(SelectOption(label=data['title'], value=data['video_id']))
        super().__init__(
            custom_id='search_select',
            placeholder='再生したい曲を選択',
            options=options,
            max_values=1,
            min_values=1
        )

    async def callback(self, inter: Interaction):
        source = await YTDLSource.from_url(f'https://www.youtube.com/watch?v={self.values[0]}')
        embed = Embed(title='再生します。', description='', color=Colour.green())
        embed.add_field(name=f'{source.title}', value=' ')
        embed.set_image(url=source.thumbnail)
        embed.set_footer(text=f'再生時間：{source.duration // 60}分{source.duration - source.duration // 60 * 60}秒')
        await audio_statuses[inter.channel.id].add_audio(source)
        await inter.message.edit(embed=embed, view=None)


class YTDLSource(PCMVolumeTransformer):
    def __init__(self, source, *, data, volume=0.02):
        super().__init__(source, volume)

        self.data = data

        self.title = data.get('title')
        self.url = data.get('url')
        self.author = data.get('uploader')
        self.duration = data.get('duration')
        self.view_count = data.get('view_count')
        self.thumbnail = data.get('thumbnail')

    @classmethod
    async def from_url(cls, url: str, *, loop=None, stream=False):
        loop = loop or asyncio.get_event_loop()
        data = await loop.run_in_executor(None, lambda: ytdl.extract_info(url, download=not stream))

        if 'entries' in data:
            # take first item from a playlist
            data = data['entries'][0]

        filename = data['url'] if stream else ytdl.prepare_filename(data)
        return cls(FFmpegPCMAudio(filename, **ffmpeg_options), data=data)

def before_invoke(f):
    @functools.wraps(f)
    async def callback(self, inter: Interaction, *args, **kwargs):
        await inter.response.defer()
        if inter.guild.voice_client is None:
            member = inter.guild.get_member(inter.user.id)
            if member.voice:
                voice_client = await member.voice.channel.connect()
                audio_statuses[inter.channel.id] = AudioStatus(inter, inter.channel, voice_client)
            else:
                await inter.followup.send("あなたはボイスチャンネルに参加していません。")
                raise commands.CommandError("Author not connected to a voice channel.")
        await f(self, inter, *args, **kwargs)

    return callback

class Music(commands.GroupCog, name='music'):
    def __init__(self, bot):
        self.bot = bot
        super().__init__()

    @app_commands.command()
    async def join(self, inter: Interaction):
        """ボイスチャンネルに接続する。"""
        member = inter.guild.get_member(inter.user.id)
        if member.voice:
            voice_client = await member.voice.channel.connect()
            audio_statuses[inter.channel.id] = AudioStatus(inter, inter.channel, voice_client)
            await inter.response.send_message("接続しました。")
        else:
            await inter.response.send_message("あなたはボイスチャンネルに参加していません。")

    @app_commands.command()
    async def volume(self, inter: Interaction, volume: int):
        """音量を変更する。"""

        if inter.guild.voice_client is None:
            return await inter.response.send_message("ボイスチャンネルに接続していません。")

        audio_statuses[inter.channel.id].vc.source.volume = volume / 100
        await inter.response.send_message(f"音量を{volume}%に変更しました。")

    @app_commands.command()
    async def pause(self, inter: Interaction):
        """音楽を一時停止する。"""
        await audio_statuses[inter.channel.id].pause()
        await inter.response.send_message('一時停止しました。')

    @app_commands.command()
    async def resume(self, inter: Interaction):
        """音楽を再開する。"""
        await audio_statuses[inter.channel.id].resume()
        await inter.response.send_message('再生を再開しました。')

    @app_commands.command(description='再生を停止し、キューをリセットします。')
    async def stop(self, inter: Interaction):
        """音楽を停止し、Queueの中身をリセットする。"""
        await audio_statuses[inter.channel.id].stop()
        await inter.response.send_message('停止しました。')

    @app_commands.command()
    async def leave(self, inter: Interaction):
        """音楽を停止し、ボイスチャンネルから切断する。"""
        await audio_statuses[inter.channel.id].vc.disconnect()
        del audio_statuses[inter.channel.id]
        await inter.response.send_message('切断しました。')

    @app_commands.command()
    @before_invoke
    async def play(self, inter: Interaction, music_name: str):
        if music_name in 'https://www.youtube.com/watch':
            source = await YTDLSource.from_url(music_name)
            await audio_statuses[inter.channel.id].add_audio(source)
        else:
            result = []
            embed = Embed(title='検索結果', description='', color=Colour.red())
            search_response = youtube.search().list(
                part='snippet',
                q=music_name,
                maxResults=10
            ).execute()
            for search_result in search_response.get('items', []):
                if search_result['id']['kind'] == 'youtube#video':
                    result.append({'title': search_result['snippet']['title'], 'video_id': search_result['id']['videoId']})
            for i, v in enumerate(result):
                embed.add_field(name=f'{i + 1}. {v["title"]}', value=f'https://www.youtube.com/watch?v={v["video_id"]}', inline=False)
            if not result:
                return await inter.followup.send(f'{music_name}は見つかりませんでした。')
            await inter.followup.send(embed=embed, view=SearchView(result, inter.channel))


async def setup(bot):
    await bot.add_cog(Music(bot))

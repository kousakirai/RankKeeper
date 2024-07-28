from discord.ext import commands
from discord import app_commands, Interaction, Embed, ClientException, Colour, SelectOption
from discord.ui import View, Select
from rank_keeper.core.core import RKCore
import wavelink
from typing import cast
from googleapiclient.discovery import build
import functools
import os


youtube = build(
    'youtube',
    'v3',
    developerKey=os.environ.get('YOUTUBE_API_KEY')
)


class SelectView(View):
    def __init__(self, player, track_data: list[dict]):
        super().__init__(timeout=None)
        self.add_item(SelectMenu(player, track_data))


def check_connected(f):
    @functools.wraps(f)
    async def callback(self, inter: Interaction, *args, **kwargs):
        await inter.response.defer()
        player: wavelink.Player = cast(wavelink.Player, inter.guild.voice_client)

        if not player:
            await inter.followup.send('あなたはボイスチャンネルに接続していません。')
            raise commands.CommandError("Author not connected to a voice channel.")
        inter.extras['player'] = player
        await f(self, inter, *args, **kwargs)

    return callback


class SelectMenu(Select):
    def __init__(self, player: wavelink.Player, track_data: list[dict]):
        self.player = player
        options = []
        for track in track_data:
            options.append(SelectOption(label=track['title'], value=track['video_id']))
        super().__init__(placeholder='再生したい曲を選択', min_values=1, max_values=1, options=options)

    async def callback(self, inter: Interaction):
        tracks = await wavelink.Playable.search('https://www.youtube.com/watch?v=' + self.values[0])
        print(type(tracks))
        if isinstance(tracks, wavelink.Playable):
            track: int = tracks[0]
            await self.player.queue.put_wait(track)
            await self.player.home.send(f'キューに **{track}** を追加しました。')
        elif isinstance(tracks, wavelink.Playlist):
            added: int = await self.player.queue.put_wait(tracks)
            await self.player.home.send(f'キューにプレイリスト：**{tracks.name}** ({added}曲)を追加しました。')
        else:
            raise Exception('Unexpected error')
        if not self.player.playing:
            await self.player.play(self.player.queue.get(), volume=30)

class MusicCog(commands.GroupCog, name='music'):
    def __init__(self, bot):
        self.bot: RKCore = bot

    @commands.Cog.listener()
    async def on_wavelink_track_start(self, payload: wavelink.TrackStartEventPayload) -> None:
        player: wavelink.Player | None = payload.player
        if not player:
            # Handle edge cases...
            return

        original: wavelink.Playable | None = payload.original
        track: wavelink.Playable = payload.track

        embed: Embed = Embed(title="Now Playing")
        embed.description = f"**{track.title}** by `{track.author}`"

        if track.artwork:
            embed.set_image(url=track.artwork)

        if original and original.recommended:
            embed.description += f"\n\n`この曲のソース：{track.source}`"

        if track.album.name:
            embed.add_field(name="アルバム", value=track.album.name)

        await player.home.send(embed=embed)

    @commands.Cog.listener()
    async def on_wavelink_track_end(self, player: wavelink.Player, track, reason):
        if not player.queue.is_empty:
            next_track = player.queue.get()
            await player.play(next_track)

    @app_commands.command(name='play')
    async def play_music(self, inter: Interaction, query: str) -> None:
        await inter.response.defer()
        if not inter.guild:
            return await inter.response.send_message("このコマンドはサーバー内でのみ実行できます。")

        player: wavelink.Player
        player = cast(wavelink.Player, inter.guild.voice_client)

        if not player:
            member = inter.guild.get_member(inter.user.id)
            try:
                player = await member.voice.channel.connect(cls=wavelink.Player)
            except AttributeError:
                return await inter.response.send_message("ボイスチャンネルに接続してから実行してください。")

            except ClientException:
                return await inter.response.send_message('ボイスチャンネルに参加することができませんでした。もう一度お試しください。')

        player.autoplay = wavelink.AutoPlayMode.enabled

        if not hasattr(player, 'home'):
            player.home = inter.channel

        elif player.home != inter.channel:
            return await inter.response.send_message(f'音楽の再生は{player.home.mention}でのみ行えます。')

        if 'https://www.youtube.com/watch?v' in query:
            tracks = await wavelink.Playable.search(query)
            if isinstance(tracks, wavelink.Playable):
                track: int = tracks[0]
                await self.player.queue.put_wait(track)
                await self.player.home.send(f'キューに **{track}** を追加しました。')
            elif isinstance(tracks, wavelink.Playlist):
                added: int = await self.player.queue.put_wait(tracks)
                await self.player.home.send(f'キューにプレイリスト：**{tracks.name}** ({added}曲)を追加しました。')
            else:
                raise Exception('Unexpected error')
            if not self.player.playing:
                await self.player.play(inter.extra['player'].queue.get(), volume=30)
        result = []
        embed = Embed(title='検索結果', description='', color=Colour.green())
        search_response = youtube.search().list(
            part='snippet',
            q=query,
            maxResults=10
        ).execute()
        for search_result in search_response.get('items', []):
            if search_result['id']['kind'] == 'youtube#video':
                result.append({'title': search_result['snippet']['title'], 'video_id': search_result['id']['videoId']})
        for i, v in enumerate(result):
            embed.add_field(name=f'{i + 1}. {v["title"]}', value=f'https://www.youtube.com/watch?v={v["video_id"]}', inline=False)

        view = SelectView(player, result)
        await inter.followup.send(embed=embed, view=view)

    @app_commands.command(name='skip')
    @check_connected
    async def skip_track(self, inter: Interaction):
        await inter.extras['player'].skip(force=True)
        await inter.followup.send('\u2705')

    @app_commands.command(name='toggle')
    @check_connected
    async def pause_resumed(self, inter: Interaction):
        await inter.extras['player'].pause(not inter.player.paused)
        if inter.extras['player'].paused:
            await inter.followup.send('\u23F8')
        else:
            await inter.followup.send('\u25B6')

    @app_commands.command(name='volume')
    @check_connected
    async def set_volume(self, inter: Interaction, volume: int):
        await inter.extras['player'].set_volume(volume)
        await inter.followup.send(f'\u2705')

    @app_commands.command(name='disconnect')
    @check_connected
    async def disconnect(self, inter: Interaction):
        await inter.extras['player'].disconnect()
        await inter.followup.send('\u2705')


async def setup(bot):
    await bot.add_cog(MusicCog(bot))
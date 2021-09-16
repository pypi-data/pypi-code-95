import time

import discord

from . import exceptions
from . import filters
from . import objects
from .node import Node
from .pool import NodePool
from . import events

import discord
from discord import VoiceProtocol, VoiceChannel
from discord.ext import commands
from typing import Optional, Any, Union



class Player(VoiceProtocol):

    def __init__(self, client: Union[commands.Bot, discord.Client, commands.AutoShardedBot, discord.AutoShardedClient], channel: VoiceChannel):
        super().__init__(client=client, channel=channel)

        self.client: discord.Client = client
        self._bot: discord.Client = client
        self.channel: VoiceChannel = channel
        self._guild: discord.Guild = channel.guild

        self._node: Node = NodePool.get_node()
        self._current: objects.Track = None
        self._filters: dict = {}
        self._volume: int = 100
        self._paused: bool = False
        self._is_connected: bool = False

        self._position: int = 0
        self._last_update: int = 0
        self._current_track_id = None


        self._session_id: Optional[str] = None
        self._voice_server_update_data: Optional[dict] = None


    def __repr__(self):
        return f"<Obsidian.player bot={self._bot} guild_id={self._guild.id} is_connected={self.is_connected} is_playing={self.is_playing}>"

    @property
    def position(self):

        if not self.is_playing:
            return 0

        if self._paused:
            return min(self._position, self._current.length)

        position = round(self._position + ((time.time() * 1000) - self._last_update))

        if position > self._current.length:
            return 0

        return position

    @property
    def is_connected(self):
        return self._is_connected

    @property
    def is_playing(self):
        return self._is_connected and self._current is not None

    @property
    def is_paused(self):
        return self._is_connected and self._paused is True

    @property
    def node(self):
        return self._node

    @property
    def current(self):
        return self._current

    @property
    def volume(self):
        return self._volume


    async def _update_state(self, state: dict):

        self._last_update = time.time() * 1000

        frames = state.get('frames', {})
        self._frames_sent = frames.get('sent')
        self._frames_lost = frames.get('lost')
        self._frame_data_usable = frames.get('usable', False)

        current_track = state.get('current_track', {})
        self._current_track_id = current_track.get('track')
        self._position = current_track.get('position', 0)
        self._paused = current_track.get('paused', False)
        self._filters = state.get('filters', {})

    async def _dispatch_voice_update(self) -> None:

        if not self._session_id or not self._voice_server_update_data:
            return

        await self._node.send(op=0, d={**{'session_id': self._session_id, **self._voice_server_update_data}})

    async def _voice_server_update(self, data: dict):

        self._voice_server_update_data = data
        await self._dispatch_voice_update()

        
    async def _voice_state_update(self, data: dict):

        if not (channel_id := data.get('channel_id')):
            self.channel, self._session_id, self._voice_server_update_data = None
            return

        self.channel = self._guild.get_channel(int(channel_id))
        self._session_id = data.get('session_id')
        await self._dispatch_voice_update()

    async def _dispatch_event(self, data: dict):
        event = getattr(events, f'{data["type"].lower().title().replace("_", "")}Event', None)
        event = event(data)
        self._bot.dispatch(f"obsidian_{event.name}", event)

    async def get_tracks(self, query: str):
        return await self._node.get_tracks(query)

    async def connect(self, *, timeout: float, reconnect: bool):
        await self._guild.change_voice_state(channel=self.channel)
        self._node._players[self._guild.id] = self
        self._is_connected = True

        
    async def stop(self):
        self._current = None
        await self._node.send(op=7, d={'guild_id': str(self._guild.id)})

    async def disconnect(self, *, force: bool = False):
        await self.stop()
        await self._guild.change_voice_state(channel=None)
        self.cleanup()
        self.channel = None
        self._is_connected = False
        del self._node._players[self._guild.id]


    async def destroy(self):
        await self.disconnect() 
        await self._node.send(op=11, d={'guild_id': str(self._guild.id)})

    async def play(self, track: objects.Track, start_position: int = 0):

        await self._node.send(op=6, d={'guild_id': str(self._guild.id), 'track' :track.track_id, 'start_time': start_position, 'end_time': track.length, 'no_replace': False})

        self._current = track
        return self._current

    async def seek(self, position: int):

        if position < 0 or position > self.current.length:
            raise exceptions.TrackInvalidPosition(f"Seek position must be between 0 and the track length")

        await self._node.send(op=10, d={'guild_id': str(self._guild.id), 'position': position})

        return self.position

    async def set_pause(self, pause: bool):

        await self._node.send(op=8, d={'guild_id': str(self._guild.id), 'state': pause})

        self._paused = pause
        return self._paused

    async def set_volume(self, volume: int):

        await self._node.send(op=9, d={'guild_id': str(self._guild.id), 'filters': {'volume': volume}})
        self._volume = volume
        return self._volume

    async def set_filter(self, filter_type: filters.Filter):
        await self._node.send(op=9, d={'guild_id': str(self._guild.id), 'filters': {**filter_type.payload}})
        await self.seek(self.position)
        return filter_type

  
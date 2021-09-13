import json
from typing import List

from down_notifier.channel import BaseChannel, TelegramChannel
from down_notifier.site import Site


class Parser:
    _available_channel_types: dict = {
        "telegram": TelegramChannel,
    }
    _channels: List[BaseChannel] = []

    def parse(self, content: str) -> List[Site]:
        obj: dict = json.loads(content)
        sites_obj = obj.get("sites")
        if sites_obj is None:
            raise RuntimeError("sites can't be None")

        channels_obj = obj.get("channels")
        if channels_obj is None:
            raise RuntimeError("channels can't be None")

        for name, config in channels_obj.items():
            channel = self._available_channel_types[config.get("type")](
                name=name,
                **config,
            )
            self._channels.append(channel)

        return [self._parse_site(name, config) for name, config in sites_obj.items()]

    def _parse_site(self, name: str, config: dict) -> Site:
        channel_names = config.get("channels")
        channels = []
        for channel in self._channels:
            if channel.name in channel_names:  # type: ignore
                channels.append(channel)

        url = config.get("url")
        status_code = config.get("status_code")
        timeout = config.get("timeout")

        return Site(name, url, status_code, timeout, channels)  # type: ignore

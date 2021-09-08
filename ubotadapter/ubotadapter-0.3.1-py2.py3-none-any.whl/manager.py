from typing import Generator, Any, Type, Dict, Union

from ubotadapter import UBotAdapter, InboundProcessor, ChannelType


class BotChannelCollection:
    def __init__(self):
        self._bots = {}

    def __iter__(self) -> Generator[UBotAdapter, Any, None]:
        return (bot for bot in self._bots.values())

    @property
    def bots(self) -> Dict[str, UBotAdapter]:
        return self._bots

    def __getitem__(self, bot_id_string: str) -> UBotAdapter:
        return self._bots[str(bot_id_string)]

    def __setitem__(self, bot_id_string: str, bot):
        bot_id_string = str(bot_id_string)
        if bot_id_string not in self._bots:
            self._bots[bot_id_string] = bot
        else:
            raise KeyError(f'Bot with id "{bot_id_string}" already exists in bot channel.')


class BotChannels:
    def __init__(self):
        self._channels = {}

    def __iter__(self) -> Generator[BotChannelCollection, Any, None]:
        return (collection for collection in self._channels.values())

    @property
    def channels(self) -> Dict[ChannelType, BotChannelCollection]:
        return self._channels

    def __getitem__(self, channel_type: ChannelType) -> BotChannelCollection:
        if channel_type not in self._channels:
            self._channels[channel_type] = BotChannelCollection()
        return self._channels[channel_type]

    def get_by_channel_name(self, channel_name: str) -> BotChannelCollection:
        try:
            channel = ChannelType[channel_name]
        except KeyError:
            raise KeyError(f'No ChannelType with name "{channel_name}" exists')
        else:
            return self[channel]


class BotsManager:
    def __init__(self):
        self._channels = BotChannels()

    def __iter__(self) -> Generator[UBotAdapter, Any, None]:
        return (b for b in self.bots)

    def __getitem__(self, channel_type: Union[ChannelType, str]) -> BotChannelCollection:
        if isinstance(channel_type, ChannelType):
            return self.channels[channel_type]
        else:
            return self.channels.get_by_channel_name(channel_type)

    def add(self, bot: UBotAdapter):
        self._channels[bot.channel][bot.config.bot_id_string] = bot

    @property
    def bots(self) -> Generator[UBotAdapter, Any, None]:
        for channel in self.channels:
            for bot in channel:
                yield bot

    @property
    def channels(self) -> BotChannels:
        return self._channels

    def get_by_channel_name_and_id(self, channel_name: str, bot_id_string: str):
        channel = self.channels.get_by_channel_name(channel_name)
        return channel[str(bot_id_string)]

    def set_inbound_processor(self, inbound_processor: Type[InboundProcessor]):
        for bot in self.bots:
            bot.set_inbound_processor(inbound_processor)

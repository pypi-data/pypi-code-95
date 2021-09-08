from typing import List, Type, Callable

import ubotadapter
from ubotadapter import InboundMessage
from ubotadapter.botcontext import BotContext
from ubotadapter.bots import *
from ubotadapter.inbound import InboundProcessor
from .test_data import *


class BadInboundProcessor(InboundProcessor):

    @staticmethod
    def process(context: BotContext, inbound: InboundMessage):
        raise ValueError("Pseudo-processing error")


def get_tg_bot(**config):
    with open(os.path.join(DATA_DIR, 'telegram.json'), 'r', encoding='utf-8') as f:
        config.update(json.load(f))
    return Telegram(config)


def get_dtf_bot(**config):
    with open(os.path.join(DATA_DIR, 'dtf.json'), 'r', encoding='utf-8') as f:
        config.update(json.load(f))
    return DTF(config)


def get_vk_bot():
    return VK(os.path.join(DATA_DIR, 'vk.json'))


class BotTestData:
    def __init__(self,
                 bot: Callable,
                 channel: ubotadapter.ChannelType,
                 message_getter: TestMessage,
                 visual_name_text: str,
                 all_message_getters: List[TestMessage]):
        self._bot = bot
        self.channel = channel
        self.message_getter = message_getter
        self.visual_name_text = visual_name_text
        self.all_message_getters = all_message_getters

    @property
    def bot(self) -> ubotadapter.UBotAdapter:
        return self._bot()


BOTS_LIBRARY: List[BotTestData] = [
    BotTestData(get_tg_bot, Telegram.channel, TGTestMessage(), 'Igor Shephard / Igor',
                [TGTestMessage(), TGCallbackTestMessage()]),

    BotTestData(get_vk_bot, VK.channel, VKTestMessage(), 'Игорь Шепард / Игорь', [VKTestMessage()]),

    BotTestData(get_dtf_bot, DTF.channel, DTFTestMessage(), 'Igor Shephard / Igor Shephard', [DTFTestMessage()])
]

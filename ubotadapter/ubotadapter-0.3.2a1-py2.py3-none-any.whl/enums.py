from enum import Enum


class ChannelType(Enum):
    Telegram = 0
    VK = 1
    Discord = 2  # not yet supported
    WhatsApp = 10  # not yet supported
    WeChat = 11  # not yet supported
    Skype = 20  # not yet supported
    DTF = 100

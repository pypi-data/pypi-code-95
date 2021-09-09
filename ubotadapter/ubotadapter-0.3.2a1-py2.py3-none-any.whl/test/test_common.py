import unittest

from ubotadapter.botmsg import Keyboard
from ubotadapter.inbound import *
from .test_tools import *


class TestKeyboardInboundProcessor(InboundProcessor):
    @staticmethod
    def process(context: BotContext, inbound: InboundMessage):
        buttons = [['button_1', 'button_2'], ['button_3']]
        context.replies.add(
            BotMessage('Choose:', keyboard=Keyboard(buttons=buttons, one_time=True, in_line=True)))
        context.replies.add(
            BotMessage('Choose!', keyboard=Keyboard(buttons=buttons, one_time=True, in_line=False)))


class TestBotsInboundProcessor(unittest.TestCase):
    def test_echo_inbound_processor(self):
        for bot_test in BOTS_LIBRARY:
            bot = bot_test.bot
            with self.subTest(bot=bot.channel.name):
                bot.set_inbound_processor(EchoInboundProcessor)
                for message_getter in bot_test.all_message_getters:
                    result = bot.handle(message_getter.get_message())
                    self.assertTrue(result.is_ok, msg=result.report())
                    self.assertFalse(result.no_replies)

    def test_reply_inbound_processor(self):
        for bot_test in BOTS_LIBRARY:
            bot = bot_test.bot
            with self.subTest(bot=bot.channel.name):
                bot.set_inbound_processor(EchoReplyToInboundProcessor)
                result = bot.handle(bot_test.message_getter.get_message(text='ut_reply_to'))
                self.assertTrue(result.is_ok, msg=result.report())
                self.assertFalse(result.no_replies)

    def test_keyboard_inbound_processor(self):
        for bot_test in BOTS_LIBRARY:
            bot = bot_test.bot
            with self.subTest(bot=bot.channel.name):
                bot.set_inbound_processor(TestKeyboardInboundProcessor)
                result = bot.handle(bot_test.message_getter.get_message())
                self.assertTrue(result.is_ok, msg=result.report())
                self.assertFalse(result.no_replies)

    def test_vk_get_name(self):
        bot = get_vk_bot()
        bot.set_inbound_processor(EchoNameInboundProcessor)
        message = VKTestMessage().get_message(bot.config.bot_id)
        result = bot.handle(message)
        self.assertTrue(bot.context.replies.count == 1)
        self.assertTrue(result.is_ok, msg=result.report())

    def test_vk_reply_to_group_chat(self):
        bot = get_vk_bot()
        bot.set_inbound_processor(EchoReplyToInboundProcessor)
        result = bot.handle(VKTestMessage().get_message(text='ut_reply_to', chat_id=2000000001, message_id=1))
        self.assertTrue(result.is_ok, msg=result.report())
        self.assertFalse(result.no_replies)

        result = bot.handle(VKTestMessage().get_message(text='ut_reply_to', message_id=1))
        self.assertTrue(result.is_ok, msg=result.report())
        self.assertFalse(result.no_replies)


if __name__ == '__main__':
    import logging

    logger = logging.getLogger('ubotadapter')
    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)
    unittest.main()

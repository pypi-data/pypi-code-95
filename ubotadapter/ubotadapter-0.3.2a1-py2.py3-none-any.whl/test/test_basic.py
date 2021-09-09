import datetime
import unittest

from ubotadapter import BotsManager
from ubotadapter.botdebug import *
from ubotadapter.msgfilter import MessageFilter
from ubotadapter.test.test_tools import *
from .test_bot import TestingInboundProcessor, MARKER


class TestBotsInit(unittest.TestCase):

    def test_vk_bot(self):
        bot = get_vk_bot()
        self.assertIsNotNone(bot)

    def test_telegram_bot(self):
        bot = get_tg_bot()
        self.assertIsNotNone(bot)

    def test_dtf_bot(self):
        bot = get_dtf_bot()
        self.assertIsNotNone(bot)


class TestBotsInboundProcessor(unittest.TestCase):

    def test_tg_inbound_processor(self):
        bot = get_tg_bot()

        result = bot.handle(TGTestMessage().get_message())
        self.assertTrue(result.is_ok, result.report())
        self.assertTrue(result.no_replies, result.report())

        result = bot.handle(TGCallbackTestMessage().get_message())
        self.assertTrue(result.is_ok, msg=result.report())
        self.assertTrue(result.no_replies)

    def test_tg_bad_inbound_processor(self):
        bot = get_tg_bot(is_send_process_error_message=False)
        bot.set_inbound_processor(BadInboundProcessor)
        result = bot.handle(TGTestMessage().get_message())
        self.assertFalse(result.is_ok)
        self.assertEqual(BotProcessStatus.unknown_error, result.process_result.status, result.process_result.exception)
        self.assertTrue(result.no_replies)

    def test_tg_bad_inbound_message(self):
        bot = get_tg_bot(is_send_process_error_message=False)
        # empty dictionary
        # with self.assertRaises(KeyError):
        result = bot.handle({})
        self.assertFalse(result.is_ok)
        self.assertEqual(result.process_result.status, BotProcessStatus.inbound_error)
        self.assertTrue(result.no_replies)

    def test_vk_inbound_processor(self):
        bot = get_vk_bot()
        msg = VKTestMessage().get_message(bot_id=bot.config.bot_id)
        result = bot.handle(msg)
        self.assertTrue(result.is_ok, f'Result: {result.report()} // Inbound: {msg}')
        self.assertTrue(result.no_replies)

    def test_vk_secret_process(self):
        bot = get_vk_bot()
        message = VKTestMessage().get_message(bot_id=bot.config.bot_id)

        # bad secret
        message['secret'] = 'bad_secret'
        result = bot.handle(message)
        self.assertEqual(result.process_result.status, BotProcessStatus.wrong_secret, msg=result.report())
        self.assertFalse(result.is_ok)

        # good secret
        message['secret'] = bot.config.webhook_secret
        result = bot.handle(message)
        self.assertEqual(result.process_result.status, BotProcessStatus.ok)
        self.assertTrue(result.is_ok)

    def test_get_name(self):
        class EchoUserDataInboundProcessor(InboundProcessor):
            @staticmethod
            def process(context: BotContext, inbound: InboundMessage):
                text = f'{inbound.user.visual_name} / {inbound.user.short_name}'
                context.replies.add_text(text)

        for bot_test in BOTS_LIBRARY:
            bot = bot_test.bot
            with self.subTest(bot=bot.channel.name):
                bot.set_inbound_processor(EchoUserDataInboundProcessor)
                message = bot_test.message_getter.get_message(bot_id=bot.config.bot_id)
                inbound = bot._init_inbound(message)
                result = bot._process(inbound)
                self.assertEqual(1, bot.context.replies.count, result.data)
                self.assertEqual(BotProcessStatus.ok, result.status, msg=result.exception)
                self.assertEqual(bot_test.visual_name_text, bot.context.replies[0].text, msg=bot.info.name)

    def test_basic_processor(self):
        """Checking test bot."""
        message_text = f'{MARKER} echo'

        for bot_test in BOTS_LIBRARY:
            bot = bot_test.bot
            with self.subTest(bot=bot.channel.name):
                bot.set_inbound_processor(TestingInboundProcessor)
                message = bot_test.message_getter.get_message(text=message_text, bot_id=bot.config.bot_id)
                inbound = bot._init_inbound(message)
                self.assertEqual(inbound.context.bot.channel, bot.channel, msg='No match of inbound and bot channel')
                result = bot._process(inbound)
                self.assertEqual(bot.context.replies.count, 1)
                self.assertEqual(result.status, BotProcessStatus.ok, msg=result.exception)
                self.assertEqual(bot.context.replies[0].text, message_text, msg=bot.info.name)

    def test_filters(self):
        class TextMessageFilter(MessageFilter):
            @staticmethod
            def is_true(context: BotContext, message: InboundMessage) -> bool:
                return message.text != 'filter_out'

        for bot_test in BOTS_LIBRARY:
            bot = bot_test.bot
            with self.subTest(bot=bot.channel.name):
                # NoBotMessage filter
                message = bot_test.message_getter.get_message(user_id=bot.config.bot_id, bot_id=bot.config.bot_id)
                inbound = bot._init_inbound(message)
                result = bot._process(inbound)
                self.assertEqual(0, bot.context.replies.count, msg=bot.context.replies)
                self.assertEqual(BotProcessStatus.filter_not_passed, result.status, msg=result.exception)

                # MessageFilter add
                bot.message_filters_manager.add_filter(TextMessageFilter)
                message = bot_test.message_getter.get_message(text='filter_out', user_id=bot.config.bot_id,
                                                              bot_id=bot.config.bot_id)
                inbound = bot._init_inbound(message)
                result = bot._process(inbound)
                self.assertEqual(bot.context.replies.count, 0)
                self.assertEqual(BotProcessStatus.filter_not_passed, result.status, msg=result.exception)

    def test_bot_manager(self):
        manager = BotsManager()
        for bot_test in BOTS_LIBRARY:
            bot = bot_test.bot
            with self.subTest(bot=bot.channel.name):
                manager.add(bot)
                bot_from_manager = manager.channels[bot.channel][bot.config.bot_id_string]
                self.assertEqual(bot.config.bot_id, bot_from_manager.config.bot_id)

        manager.set_inbound_processor(InboundProcessor)

    def test_tg_inbound_reply(self):
        bot = get_tg_bot()
        message = TG_MESSAGE_REPLY
        inbound = bot._init_inbound(message)
        self.assertIsNotNone(inbound)
        self.assertIsNotNone(inbound.text)
        self.assertIsNotNone(inbound.reply_to_msg.message_id)
        self.assertTrue(isinstance(inbound.reply_to_msg.user_visual_name, str))
        self.assertTrue(isinstance(inbound.reply_to_msg.date, datetime.datetime))

    def test_vk_inbound_reply(self):
        bot = get_vk_bot()
        message = VK_MESSAGE_REPLY
        inbound = bot._init_inbound(message)
        self.assertIsNotNone(inbound)
        self.assertIsNotNone(inbound.text)
        self.assertIsNotNone(inbound.reply_to_msg.message_id)
        self.assertTrue(isinstance(inbound.reply_to_msg.user_visual_name, str))
        self.assertTrue(isinstance(inbound.reply_to_msg.date_raw, int))
        self.assertTrue(isinstance(inbound.reply_to_msg.date, datetime.datetime))

    def test_dtf_inbound_reply(self):
        bot = get_dtf_bot()
        message = DTF_MESSAGE_REPLY
        inbound = bot._init_inbound(message)
        self.assertIsNotNone(inbound)
        self.assertIsNotNone(inbound.text)
        self.assertIsNotNone(inbound.reply_to_msg.message_id)
        self.assertTrue(isinstance(inbound.reply_to_msg.user_visual_name, str))
        self.assertTrue(isinstance(inbound.date_raw, str), msg=f'date_raw: {inbound.reply_to_msg.date_raw}')
        self.assertTrue(isinstance(inbound.date, datetime.datetime))


if __name__ == '__main__':
    import logging
    from ubotadapter.logger import logger

    logger.addHandler(logging.StreamHandler())
    logger.setLevel(logging.DEBUG)
    unittest.main()

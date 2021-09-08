import unittest

from ubotadapter.test.test_tools import *


class TestWebhooks(unittest.TestCase):
    def test_webhooks(self):
        for bot_test in BOTS_LIBRARY:
            bot = bot_test.bot
            with self.subTest(bot=bot.channel.name):
                # delete
                is_ok = bot.disable_webhook()
                self.assertTrue(is_ok, msg='Can\'t disable webhook')
                # check
                is_ok, url = bot.check_webhook()
                self.assertFalse(is_ok, msg='Webhook should be disabled')
                # update
                is_ok, url = bot.update_webhook()
                self.assertTrue(is_ok, msg=(is_ok, url))
                self.assertEqual(url, bot.config.webhook_url, msg=(is_ok, url))
                # delete
                is_ok = bot.disable_webhook()
                self.assertTrue(is_ok, msg='Can\'t disable webhook')


if __name__ == '__main__':
    unittest.main()

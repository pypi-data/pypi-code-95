from decouple import config
from requests.exceptions import HTTPError

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from battlenet_client.client import BattleNetClient
from battlenet_client.constants import UNITED_STATES, WOW
from battlenet_client.exceptions import *


class CredentialClientTests(unittest.TestCase):

    def setUp(self):
        self.connection = BattleNetClient(UNITED_STATES, WOW, config('CLIENT_ID'), config('CLIENT_SECRET'))

    def test_get_not_found(self):
        self.assertRaises(BNetDataNotFoundError,
                          lambda: self.connection.api_get(
                              f'{self.connection.api_host}/data/wow/playable-class/-1', 'en_US', 'static'))

    def test_get_found(self):
        self.assertIsInstance(self.connection.api_get(
                              f'{self.connection.api_host}/data/wow/playable-class/1', 'enus', 'static'), dict)

    def test_post_not_found(self):
        self.assertRaises(BNetDataNotFoundError,
                          lambda: self.connection.api_post(f'{self.connection.api_host}/data/wow/playable-class/-1',
                                                           'en_US', 'static'))

    def test_post_invalid(self):
        self.assertRaises(BNetDataNotFoundError,
                          lambda: self.connection.api_post(f'{self.connection.api_host}/data/wow/playable-class/1',
                                                           'enus', 'static'))

    def tearDown(self):
        self.connection.close()

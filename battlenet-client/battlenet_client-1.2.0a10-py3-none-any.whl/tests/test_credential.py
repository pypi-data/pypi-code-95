from decouple import config
from requests.exceptions import HTTPError

try:
    import unittest2 as unittest
except ImportError:
    import unittest

from battlenet_client.client import BattleNetClient


class CredentialClientTests(unittest.TestCase):

    def setUp(self):
        self.connection = BattleNetClient('us', "wow", 'enus', config('CLIENT_ID'), config('CLIENT_SECRET'))

    def test_not_found(self):
        self.assertRaises(HTTPError,
                          lambda: self.connection.get('data/wow/playable-class/-1', locale='en_US',
                                                      namespace='static-us'))

    def test_found(self):
        self.assertIsInstance(self.connection.get('data/wow/playable-class/1', locale='en_US',
                                                  namespace='static-us'), dict)

    def tearDown(self):
        super().tearDown()



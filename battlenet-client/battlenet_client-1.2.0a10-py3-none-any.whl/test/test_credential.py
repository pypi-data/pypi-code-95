import battlenet_client
from requests.exceptions import HTTPError
from decouple import config

try:
    import unittest2 as unittest
except ImportError:
    import unittest as unittest


class CredentialClientTests(unittest.TestCase):

    def setUp(self):
        _client_id = config('CLIENT_ID')
        _client_secret = config('CLIENT_SECRET')
        self.connection = battlenet_client.BattleNetClient('us', locale='en_US', client_id=_client_id,
                                                           client_secret=_client_secret)

    def test_not_found(self):
        self.assertRaises(HTTPError,
                          lambda: self.connection.get('data/wow/playable-class/-1', locale='en_US',
                                                      namespace='static-us'))

    def test_found(self):
        self.assertIsInstance(self.connection.get('data/wow/playable-class/1', locale='en_US',
                                                  namespace='static-us'), dict)

    def tearDown(self):
        pass

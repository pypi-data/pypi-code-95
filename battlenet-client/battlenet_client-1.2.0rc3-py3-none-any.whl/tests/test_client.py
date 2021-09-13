from decouple import config
from requests.exceptions import HTTPError

try:
    import unittest2 as unittest
except ImportError:
    import unittest as unittest

from battlenet_client.client import BattleNetClient


class CredentialClientTests(unittest.TestCase):

    def setUp(self):
        self.connection = BattleNetClient('us', "wow", config('CLIENT_ID'), config('CLIENT_SECRET'))

    def test_not_found(self):
        self.assertRaises(HTTPError,
                          lambda: self.connection.get('data/wow/playable-class/-1', params={'locale': 'en_US',
                                                                                            'namespace': 'static-us'}))

    def test_found(self):
        data = self.connection.get('data/wow/playable-class/1', params={'locale': 'en_US', 'namespace': 'static-us'})
        self.assertIsInstance(data, dict)

    def test_is_warrior(self):
        data = self.connection.get('data/wow/playable-class/1', params={'locale': 'en_US', 'namespace': 'static-us'})
        self.assertEqual(data['id'], 1)
        self.assertEqual(data['name'], 'Warrior')
        self.assertEqual(data['power_type']['name'], 'Rage')
        self.assertIsInstance(data['specializations'], list)
        self.assertListEqual([spec['id'] for spec in data['specializations']], [71, 72, 73])

    def tearDown(self):
        self.connection.close()


class AuthorizationClientTests(unittest.TestCase):
    pass

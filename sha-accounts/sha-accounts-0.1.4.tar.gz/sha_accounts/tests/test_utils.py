from django.test import TestCase
from ..utils.jwt import JwtHelper


class UtilsTestCase(TestCase):
    def setUp(self):
        pass

    def test_encode_decode_jwt(self):
        p={'user':{'id':1},'user2':2}
        token=JwtHelper.encode(p)
        self.assertIsNotNone(token)
        payload=JwtHelper.decode(token)
        self.assertIsNotNone(payload)
        self.assertEqual(p,payload)
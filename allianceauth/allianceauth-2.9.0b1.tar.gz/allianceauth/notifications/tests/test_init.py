from django.test import TestCase
from allianceauth.tests.auth_utils import AuthUtils

from .. import notify
from ..models import Notification

MODULE_PATH = 'allianceauth.notifications'


class TestUserNotificationCount(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.user = AuthUtils.create_user('magic_mike')
        AuthUtils.add_main_character(
            cls.user,
            'Magic Mike',
            '1',
            corp_id='2',
            corp_name='Pole Riders',
            corp_ticker='PRIDE',
            alliance_id='3',
            alliance_name='RIDERS'
        )

    def test_can_notify(self):
        notify(self.user, 'dummy')
        self.assertEqual(Notification.objects.filter(user=self.user).count(), 1)

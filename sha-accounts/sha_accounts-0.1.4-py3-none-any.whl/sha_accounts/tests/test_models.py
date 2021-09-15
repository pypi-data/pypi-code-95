from django.test import TestCase
from ..models import User, Permission


class UserModelTestCase(TestCase):
    def setUp(self):
        pass

    def test_create_normal_user(self):
        normal_user = User.objects.create(
            username='normal', email='normal@example.com', password='normal')
        self.assertIsNotNone(normal_user)
        self.assertIsNotNone(normal_user.permissions.all())
        self.assertIsNotNone(normal_user.profile)

    def test_create_superuser(self):
        superuser = User.objects.create_superuser(
            username='superuser', email='superuser@example.com', password='superuser')
        self.assertIsNotNone(superuser)
        self.assertIsNotNone(superuser.permissions.all())
        self.assertIsNotNone(superuser.profile)

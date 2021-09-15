from django.test import TestCase
from ..serializers.user_serializers import UserSignUpRequest, UserSignUpResponse
from ..models.permission_models import Permission
from ..models import get_user_profile_model


class UserSerializerTestCase(TestCase):
    def setUp(self):
        pass

    def test_usersignuprequest_serializer(self):
        new_data = {
            'username': 'ali',
            'email': 'ali@examplle.com',
            'password': '3ecret'
        }
        serializer = UserSignUpRequest(data=new_data)
        serializer.is_valid(raise_exception=True)
        new_user = serializer.save()
        self.assertIsNotNone(new_user)
        self.assertIsInstance(new_user.profile, get_user_profile_model())
        for permission in new_user.permissions.all():
            self.assertIsInstance(permission, Permission)
        return new_user

    def test_usersignupresponse_serializer(self):
        user = self.test_usersignuprequest_serializer()
        serializer = UserSignUpResponse(user)
        self.assertIsNotNone(serializer)

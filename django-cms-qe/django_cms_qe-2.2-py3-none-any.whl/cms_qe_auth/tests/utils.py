from django.contrib.auth import get_user_model
from django.contrib.auth.backends import ModelBackend


class TestAuthBackend(ModelBackend):
    def authenticate(self, username=None, password=None):
        User = get_user_model()
        try:
            user = User.objects.get(username=username)
            return user
        except User.DoesNotExist:
            return

from django.conf import settings
from django.contrib.auth import get_user_model
from redis import Redis
from rest_framework import exceptions
from rest_framework.authentication import TokenAuthentication, BaseAuthentication

from ..redis import REDIS_CONNECTION_POOL


class NoAuthentication(BaseAuthentication):
    def authenticate(self, request):
        return None


class RedisTokenAuthentication(TokenAuthentication):
    keyword = 'Token'

    def __init__(self, *args, **kwargs):
        self.model = get_user_model()
        self.redis = Redis(connection_pool=REDIS_CONNECTION_POOL)
        super(RedisTokenAuthentication, self).__init__(*args, **kwargs)

    def get_model(self):
        """
        ### 父类中的方法，这里不需要。
        :return:
        """
        pass

    def authenticate_credentials(self, key):
        """
        重写父类方法，通过redis来实现认证。
        :param key:
        :return:
        """
        redis_key = settings.IACS_SETTINGS["LOGIN_TOKEN_KEY"].format(token=key)
        user_id = self.redis.hget(redis_key, 'id')
        try:
            user_id = int(user_id)
        except Exception:
            raise exceptions.AuthenticationFailed('Invalid token')
        try:
            user = self.model.objects.get(pk=user_id)
            user.authenticate()
        except self.model.DoesNotExist:
            raise exceptions.AuthenticationFailed('Invalid token.')

        if not user.is_active:
            raise exceptions.AuthenticationFailed('User is inactive.')
        return user, key

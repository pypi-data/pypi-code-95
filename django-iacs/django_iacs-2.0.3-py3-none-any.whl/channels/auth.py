from channels.db import database_sync_to_async
from channels.exceptions import DenyConnection
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings
from django.contrib.auth import get_user_model

from ngs.tools.channels import RedisConnection


class AsyncJsonWebSocketConsumerExtension(AsyncJsonWebsocketConsumer):
    """
    在AsyncJsonWebsocketConsumer类基础上添加token认证
    """
    user = None
    token = None
    message = dict(id=None, content=None)

    def __init__(self, *args, **kwargs):
        self.user_model = get_user_model()
        super(AsyncJsonWebSocketConsumerExtension, self).__init__(*args, **kwargs)

    async def authenticate(self):
        token = self.scope.get('subprotocols')[0:1]
        if isinstance(token, list):
            token = token[0]
        key = settings.IACS_SETTINGS["LOGIN_TOKEN_KEY"].format(token=token)
        async with RedisConnection(self.channel_layer) as redis:
            user_id = await redis.hget(key, 'id')
        try:
            user_id = int(user_id)
        except Exception:
            raise DenyConnection('Invalid token')
        try:
            user = await self.get_user(user_id)
        except self.user_model.DoesNotExist:
            raise DenyConnection('Invalid token.')
        if not user.is_active:
            raise DenyConnection('User is inactive.')
        self.user = user
        self.token = token

    @database_sync_to_async
    def get_user(self, user_id):
        return self.user_model.objects.get(id=user_id)

    async def connect(self):
        try:
            await self.authenticate()
        except DenyConnection:
            await self.close()

        if self.token is not None:
            await self.accept(self.token)
        else:
            await self.close()

    async def disconnect(self, code):
        self.token = None
        self.user = None

    async def return_data(self, serializer_class, **kwargs):
        serializer = serializer_class(data=kwargs)
        serializer.is_valid(raise_exception=True)
        await self.send_json(serializer.data)

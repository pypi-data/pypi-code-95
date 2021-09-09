import asyncio
import importlib

from channels.exceptions import DenyConnection
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from django.conf import settings
from django.contrib.auth import get_user_model
from ngs.tools.channels import RedisConnection
from ngs.tools.logs import ErrorLog
from rest_framework.exceptions import ValidationError

from .messages.serializers import RequestMessageHeader, HeaderErrorResponse
from ..log import IacsLogger


class MessageConsumer(AsyncJsonWebsocketConsumer, metaclass=IacsLogger):

    def __init__(self, *args, **kwargs):
        super(AsyncJsonWebsocketConsumer, self).__init__(*args, **kwargs)
        self.UserModel = get_user_model()
        self.channel_group_name = settings.IACS_SETTINGS["GROUP_CHANNEL_NAME"]
        self.routes = None
        self.auth_keyword = 'Token'
        self.user = None
        self.token = None
        self._load_message_routes()

    def _load_message_routes(self):
        module = importlib.import_module(settings.IACS_SETTINGS["ROOT_WEBSOCKET_MESSAGE_ROUTE"])
        self.routes = getattr(module, 'routes', {})

    def get_token_in_header(self):
        token = self.scope.get('subprotocols')[0:1]
        if isinstance(token, list):
            token = token[0]
        return token

    async def authenticate(self, token):
        key = settings.IACS_SETTINGS["LOGIN_TOKEN_KEY"].format(token=token)
        async with RedisConnection(self.channel_layer) as redis:
            try:
                user_id = await redis.hget(key, 'id')
                user_id = int(user_id)
                loop = asyncio.get_running_loop()
                # self.UserModel.objects.get(id=user_id)
                user = await loop.run_in_executor(None, self.get_user, user_id)
            except Exception as e:
                self.logger.error(f'描述: Websocket认证失败; Token: {token}')
                self.logger.exception(e)
                raise DenyConnection('Invalid token')
        if not user.is_active:
            self.logger.error(f'描述: 用户未激活; 用户ID: {user_id}')
            raise DenyConnection('user is inactive.')
        self.user = user
        self.token = token

    def get_user(self, user_id):
        return self.UserModel.objects.get(id=user_id)

    async def connect(self):
        try:
            await self.authenticate(self.get_token_in_header())
            await self.accept(self.get_token_in_header())
            await self.channel_layer.group_add(
                self.channel_group_name,
                self.channel_name
            )
            await self.channel_layer.group_add(
                settings.IACS_SETTINGS["USER_CHANNEL_NAME"].format(user_id=self.user.id),
                self.channel_name
            )
        except DenyConnection:
            await self.close()

    def get_message_route(self, msg_type):
        route = self.routes.get(msg_type)
        return route

    async def receive_json(self, content, **kwargs):
        try:
            header_serializer = RequestMessageHeader(data=content)
            if header_serializer.is_valid():
                msg_id, msg_type = header_serializer.data['msg_id'], header_serializer.data['msg_type']
                if msg_type in self.routes.keys():
                    route = self.routes.get(msg_type)
                    serializer_class, handler_class = route[:2]
                    serializer = serializer_class(data=content)
                    if serializer.is_valid():
                        handler = handler_class(
                            channel_name=self.channel_name,
                            channel_group_name=self.channel_group_name,
                            route=route
                        )
                        data = await handler.do(**serializer.data, context=self)
                        data.update({'msg_id': msg_id})
                        await self.response(data, route)
                    else:
                        await self.invalid_params(msg_id, serializer, route)
                else:
                    # todo: 错误的消息类型
                    await self.invalid_header(**{
                        'msg_id': msg_id,
                        'origin': content,
                        'errors': ValidationError({'msg_type': [f'错误的消息类型, {msg_type}']}).detail
                    })
            else:
                await self.invalid_header(**{
                    'origin': content,
                    'errors': header_serializer.errors
                })
        except Exception as e:
            self.logger.exception(e)

    async def invalid_header(self, **kwargs):
        serializer = HeaderErrorResponse(data=kwargs)
        serializer.is_valid(raise_exception=True)
        await self.send_json(serializer.data)

    async def invalid_params(self, msg_id, serializer, route):
        response_serializer_class, _ = route[2:]
        await self.response({
            'msg_id': msg_id,
            'msg_type': response_serializer_class.Meta.MSG_TYPE,
            'errors': serializer.errors,
            'result_code': response_serializer_class.ResultCode.ILLEGAL_PARAMS
        }, route)

    async def response(self, data, route):
        serializer_class, handler_class = route[2:]
        response_serializer = serializer_class(data=data)
        if response_serializer.is_valid(raise_exception=True):
            if handler_class is not None:
                handler = handler_class(channel_name=self.channel_name,
                                        channel_group_name=self.channel_group_name,
                                        route=route)
                result = await handler.do(serializer=response_serializer)
                return await self.send_json(result)

            return await self.send_json(response_serializer.data)

    async def send_message(self, data):
        """
        接收channel layer group send消息
        :param data:
        :return:
        """
        try:
            message = data.get('message')
            self.logger.debug(f'Channel message: {data}')
            msg_type = message.get('msg_type')
            route = self.routes.get(msg_type)
            await self.response(message, route)
        except Exception as e:
            self.logger.error(ErrorLog(f"无法识别的websocket消息; {data}"))
            self.error.exception(e)

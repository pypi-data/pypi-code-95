import asyncio
import re

from django.conf import settings
from ngs.tools.channels import RedisConnection

from ..auth import AsyncJsonWebSocketConsumerExtension
from ..messages.handler import BaseHandler
from ..messages.messages import UserPingResponse
from ...serializers.operation_log import OperationLogSerializer
from ...utils.time import get_current_time_by_microsecond


class ServerTimeRequestHandler(BaseHandler):
    async def do(self, *args, **kwargs):
        return {
            'time': get_current_time_by_microsecond(),
            'result_code': self.response_serializer_class.ResultCode.NORMAL
        }


class UserPingRequestHandler(BaseHandler):
    group_name = settings.IACS_SETTINGS["LOGIN_CHANNEL_GROUP_NAME"]

    async def do(self, *args, **kwargs):
        context = kwargs.get('context')
        self.channel_group_name = settings.IACS_SETTINGS["GROUP_CHANNEL_NAME"]
        token = kwargs.get('token')
        async with RedisConnection(self.channel_layer) as redis:
            redis_token = await redis.hgetall(
                settings.IACS_SETTINGS["LOGIN_TOKEN_KEY"].format(token=token),
            )
            now = get_current_time_by_microsecond()
            if redis_token:
                temp_user = await redis.hgetall(
                    settings.IACS_SETTINGS["LOGIN_USER_KEY"].format(user_id=redis_token.get(b'id').decode()))
                user_key_token = temp_user.get(b'token').decode()
                user_new_data = await redis.hgetall(
                    settings.IACS_SETTINGS["LOGIN_TOKEN_KEY"].format(token=user_key_token))
                if user_key_token != token:
                    return {'result_code': UserPingResponse.ResultCode.ANTHER_LOGIN,
                            'msg_id': get_current_time_by_microsecond(),
                            'msg_type': UserPingResponse.Meta.MSG_TYPE,
                            'time': now,
                            'data': f"用户在{user_new_data.get(b'client_host').decode()}登录"
                            }
                else:
                    return {
                        'result_code': UserPingResponse.ResultCode.NORMAL,
                        'time': now,
                    }
            else:
                await redis.delete(settings.IACS_SETTINGS["LOGIN_USER_KEY"].format(user_id=redis_token.get('id')))
                ipv4 = context.scope.get('headers')[0][1].decode().split(':')[0]
                if self.check_ipv4(ipv4):
                    data = {
                        'username': context.user.username,
                        'ipv4': ipv4,
                        'desc': '超时退出系统'
                    }
                else:
                    data = {
                        'username': context.user.username,
                        'desc': '超时退出系统'
                    }
                    loop = asyncio.get_running_loop()
                    loop.run_in_executor(None, self.save_operation_log, data)
                return {
                    'result_code': UserPingResponse.ResultCode.ERROR,
                    'time': now
                }

    def save_operation_log(self, data):
        serializer = OperationLogSerializer(data=data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

    def check_ipv4(self, ipv4):
        if re.match(r"^(?:(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)\.){3}(?:25[0-5]|2[0-4][0-9]|[01]?[0-9][0-9]?)$",
                    ipv4):
            return True
        else:
            return False


class UserPingResponseHandler(BaseHandler, AsyncJsonWebSocketConsumerExtension):

    async def do(self, *args, **kwargs):
        pass

    async def another_login(self, *args, **kwargs):
        #  检测到其它登录时自动退出登录
        if 'serializer' in kwargs.keys():
            content = kwargs.get('serializer')
            user_id = content.get('id')
            username = content.get('username')
            token = content.get('token')
            async with RedisConnection(settings.IACS_SETTINGS["LOGIN_TOKEN_KEY"].format(token=token)) as redis:
                client_host = await redis.hget(
                    settings.IACS_SETTINGS["LOGIN_TOKEN_KEY"].format(token=token),
                    'client_host'
                )
                if client_host != content.get('client_host'):
                    # 退出登录
                    await self.channel_layer.group_discard(self.channel_group_name.format(username=username),
                                                           self.channel_name)
                    await redis.hdel(settings.IACS_SETTINGS["LOGIN_USER_KEY"].format(user_id=user_id), token)
                    await self.sign_out(*args, **kwargs)
                    return {'result_code': UserPingResponse.ResultCode.ANTHER_LOGIN,
                            'msg_id': get_current_time_by_microsecond(),
                            'msg_type': UserPingResponse.Meta.MSG_TYPE,
                            'data': {
                                'msg': '用户在其它地方登录',
                                'ip': content.get('client_host')
                            }}

    async def sign_out(self, *args, **kwargs):
        """
        单点登录控制
        :return:
        """
        content = kwargs.get('serializer')
        key = settings.IACS_SETTINGS["LOGIN_USER_KEY"].format(user_id=content.get('id'))
        # 删除token
        await (await self.redis()).hdel(key, content.get('token'))
        await (await self.redis()).delete(settings.IACS_SETTINGS["LOGIN_TOKEN_KEY"].format(token=content.get('token')))

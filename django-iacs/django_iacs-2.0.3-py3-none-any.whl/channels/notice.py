from typing import Dict

from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer
from django.conf import settings


def user_notice(user_id: int, msg: Dict):
    layer = get_channel_layer()
    channel_name = settings.IACS_SETTINGS["USER_CHANNEL_GROUP_NAME"]
    async_to_sync(layer.group_send(
        channel_name.format(user_id=user_id),
        {'type': 'send.message', 'message': msg}
    ))


def broadcast(msg: Dict):
    layer = get_channel_layer()
    async_to_sync(layer.group_send(
        settings.IACS_SETTINGS["GROUP_CHANNEL_NAME"],
        {'type': 'send.message', 'message': msg}
    ))

# -*- coding: utf-8 -*-
import os
import time
import ssl

from rqdatac.validators import ensure_list_of_string
from rqdatac.decorators import export_as_api, retry

try:
    from orjson import dumps as json_dumps, loads as json_loads
except ImportError:
    try:
        import rapidjson as json
    except ImportError:
        import json
    def json_dumps(*args, **kwargs):
        return json.dumps(*args, **kwargs).encode('utf-8')

    def json_loads(*args, **kwargs):
        return json.loads(*args, **kwargs)

@export_as_api
class LiveMarketDataClient():
    def __init__(self, ws_server_uri="wss://rqdata.ricequant.com/live_md"):
        """websocket对象初始化

        :param ws_server_uri: websocket服务地址, 如 wss://rqdata.ricequant.com/live_md

        """
        self._info = None
        self._client = None
        self._ws_server_uri = ws_server_uri
        self._subscribed = set()
        self._init_websocket_client(self._ws_server_uri)

    def _init_websocket_client(self, ws_server_uri):
        from rqdatac.client import get_client
        _token = get_client().execute(
            "user.get_live_md_auth_token",
        )

        try:
            import websocket
        except ImportError:
            raise ImportError(
                "LiveMarketDataClient requires websocket-client package; run 'pip install websocket-client' to fix.")

        login_data = {
            "action": "auth_by_token",
            "token": _token
        }
        _websocket_client = websocket.WebSocket()
        self._client = _websocket_client
        retry(suppress_exceptions=(websocket.WebSocketException,), count=3)(self._websocket_login)(login_data)

    def _websocket_login(self, login_data):
        self._client.connect(self._ws_server_uri)
        self._client.send(json_dumps(login_data))
        res = self._client.recv()
        self._info = json_loads(res)


    @property
    def info(self):
        return self._info

    def subscribe(self, channels):
        """订阅实时行情

        :param channels: 订阅的标的列表 分钟和tick分别以 bar_ 和tick_开头 以平安银行为例，
            subscribe('bar_000001.XSHE')  # 订阅分钟线的实时行情
            subscribe('tick_000001.XSHE')  # 订阅tick的实时行情
            可以同时订阅多支标的 subscribe(['bar_000001.XSHE'， 'bar_000002.XSHE')

        """
        channels = ensure_list_of_string(channels)
        data = {
            "action": "subscribe",
            "channels": channels,
        }
        self._client.send(json_dumps(data))

    def unsubscribe(self, channels):
        """取消订阅实时行情

        :param channels: 取消订阅的标的列表 分钟和tick分别以 bar_ 和tick_开头 以平安银行为例，
            unsubscribe('bar_000001.XSHE')  # 订阅分钟线的实时行情
            unsubscribe('tick_000001.XSHE')  # 订阅tick的实时行情

        """
        channels = ensure_list_of_string(channels)
        data = {
            "action": "unsubscribe",
            "channels": channels,
        }
        self._client.send(json_dumps(data))

    def _reconnect(self):
        self._init_websocket_client(self._ws_server_uri)
        self.subscribe(list(self._subscribed))

    def listen(self):
        """获取订阅实时行情

        :returns: 实时行情信息

        """
        from websocket import WebSocketException
        while True:
            try:
                res = self._client.recv()
                if res:
                    data = json_loads(res)
                    if data['action'] == 'feed':
                        yield data
                    elif data['action'] == 'subscribe_reply':
                        self._subscribed.update(data['subscribed'])
                    elif data['action'] == 'unsubscribe_reply':
                        self._subscribed -= set(data['unsubscribed'])
                time.sleep(0.1)
            except WebSocketException:
                self._reconnect()

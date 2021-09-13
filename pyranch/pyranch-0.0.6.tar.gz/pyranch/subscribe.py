from base64 import b64encode
try:
    # Python 3
    from urllib.parse import urljoin
except (ImportError) as e:
    # Python 2
    from urlparse import urljoin

import websocket

from .common import CattleObject


class Subscribe(CattleObject):
    object_url = 'subscribe'

    def __init__(self, environment, event_names='resource.change', on_open = None, on_message = None, on_error = None, on_close = None):
        self.env = environment
        self.event_names = event_names
        self.service_url = '{}?eventNames={}'.format(self.object_url, self.event_names)

        # Callbacks
        self.on_open = on_open
        self.on_message = on_message
        self.on_error = on_error
        self.on_close = on_close

        # Websocket
        url = urljoin(self.env.endpoint, self.service_url)
        url = url.replace('http://', 'ws://').replace('https://', 'wss://')
        self.ws = websocket.WebSocketApp(url,
                                         header=["Authorization: Basic " + b64encode(b':'.join(self.env.auth)).strip()],
                                         on_message = self.on_message,
                                         on_error = self.on_error,
                                         on_close = self.on_close,
                                         on_open=self.on_open)

    def connect(self, ping_interval=5):
        self.ws.run_forever(ping_interval=ping_interval)

    def disconnect(self):
        self.ws.close()

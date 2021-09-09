from functools import cached_property


class BotConfig:
    __slots__ = ('_data', '__dict__')

    def __init__(self, data):
        self._data = data

    def __getitem__(self, key):
        return self._data[key]

    @property
    def token(self) -> str:
        return self['token']

    @property
    def webhook_url(self) -> str:
        return self['webhook_url']

    @property
    def webhook_secret(self):
        return self.get('webhook_secret', None)

    @property
    def is_send_process_error_message(self):
        """Send error message on processing error step"""
        return self.get('is_send_process_error_message', True)

    @property
    def bot_id(self):
        return self['bot_id']

    @cached_property
    def bot_id_string(self):
        return str(self.bot_id)

    @property
    def name(self) -> str:
        return self._data.get('name', '')


    def get(self, key, default_value=None):
        return self._data.get(key, default_value)

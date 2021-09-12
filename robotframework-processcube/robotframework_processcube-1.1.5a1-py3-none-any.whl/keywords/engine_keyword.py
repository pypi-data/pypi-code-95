from ._retry_helper import retry_on_exception


class EngineKeyword:

    def __init__(self, client, **kwargs):
        self._client = client

    @retry_on_exception
    def get_engine_info(self):
        info = self._client.info()

        return info

from alfa_sdk.common.base import BaseClient


class CacheClient(BaseClient):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def store_value(self, key, value, ttl=3600):
        body = {"key": key, "value": value, "ttl": ttl}
        return self.session.request("post", "core", "/api/caches/"+key, json=body)

    def fetch_value(self, key):
        return self.session.request("get", "core", "/api/caches/"+key)

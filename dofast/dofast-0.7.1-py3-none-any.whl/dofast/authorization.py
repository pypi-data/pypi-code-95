#!/usr/bin/env python
import redis
from cryptography.fernet import Fernet


class Authorization(Fernet):
    def __init__(self, redis_host: str, redis_port: int, redis_password: str,
                 fernet_key: bytes):
        self.redis = redis.StrictRedis(host=redis_host, 
                                       port=redis_port,
                                       password=redis_password)
        self.fernet = Fernet(fernet_key)

    def get(self, key: str) -> str:
        '''Get value from redis and decrypt with fernet.'''
        _value = self.redis.get(key)
        return self.fernet.decrypt(_value).decode()

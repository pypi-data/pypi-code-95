# -*- coding: UTF-8 -*-
from collections import defaultdict
from .backendint import BackendInterface

STRATEGY = 'always-hit'
BACKENDS = defaultdict(dict)

__all__ = ['STRATEGY', 'BACKENDS']


class GeneralBackend(BackendInterface):
    def __init__(self, config):
        super(GeneralBackend, self).__init__(config)

    def check_allowed(self, eventname, limit, timespan, increment):
        return False, 0


BACKENDS[STRATEGY]['memory'] = GeneralBackend
BACKENDS[STRATEGY]['redis'] = GeneralBackend
BACKENDS[STRATEGY]['aioredis'] = GeneralBackend
BACKENDS[STRATEGY]['sqlalchemy'] = GeneralBackend

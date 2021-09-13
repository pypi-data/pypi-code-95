import abc
import logging


class Middleware(abc.ABC):
    def __init__(self):
        self.logger = logging.getLogger('http_middleware')

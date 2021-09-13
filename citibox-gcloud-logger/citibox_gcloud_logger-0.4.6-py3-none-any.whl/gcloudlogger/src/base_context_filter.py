import logging

import abc


class BaseContextFilter(abc.ABC, logging.Filter):
    @abc.abstractmethod
    def to_dict(self) -> dict:
        pass

    @staticmethod
    @abc.abstractmethod
    def filter_name():
        pass

    def filter(self, record):
        for attribute, value in self.to_dict().items():
            setattr(record, attribute, value)
        return True


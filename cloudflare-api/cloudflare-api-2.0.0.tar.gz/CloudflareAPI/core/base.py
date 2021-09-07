#!/usr/bin/env python3

from typing import Dict
from dataclasses import dataclass

from .network import Request
from .configuration import config


class MetaBase(type):
    def __init__(cls, *args, **kwargs):
        cls.__account_id = None

    @property
    def account_id(cls) -> str:
        return cls.__account_id

    @account_id.setter
    def account_id(cls, id: str) -> None:
        cls.__account_id = id


@dataclass
class CFBase(metaclass=MetaBase):
    def props(self) -> Dict[str, str]:
        return self.__dict__

    def get_request(self, path: str):
        return Request(token=config.token(), path=path)

    def parse_params(self, params: Dict[str, str]):
        parsed = {}
        if params is not None:
            for key, value in params.items():
                if value:
                    parsed.update({key: value})
        return parsed

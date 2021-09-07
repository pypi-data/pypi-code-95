#!/usr/bin/env python3

from typing import Dict
from dataclasses import dataclass

from .network import Request
from .configuration import config


@dataclass
class CFBase:
    def props(self) -> Dict[str, str]:
        return self.__dict__

    def get_request(self, path: str) -> Request:
        return Request(token=config.token(), path=path)

    def parse_params(self, params: Dict[str, str]) -> Dict[str, str]:
        parsed = {}
        if params is not None:
            for key, value in params.items():
                if value:
                    parsed.update({key: value})
        return parsed

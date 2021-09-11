#!/usr/bin/env python3

from requests import Session
from typing import Dict, Optional

from .network import Request
from .configuration import Config


config = Config()


class CFBase:
    def verify_token(self, token) -> bool:
        url = "https://api.cloudflare.com/client/v4/user/tokens/verify"
        session = Session()
        session.headers.update({"Authorization": f"Bearer {token}"})
        response = session.get(url).json()
        if response["success"] and "result" in response:
            result = response["result"]
            if "status" in result:
                return result["status"] == "active"
        return False

    def validate(self, token: Optional[str] = None):
        if token is not None:
            config.token = token
        while not self.verify_token(config.token):
            print("Error: Invalid API Token", end="\n\n")
            config.read_from_user()

    def props(self) -> Dict[str, str]:
        return self.__dict__

    def get_request(self, path: str) -> Request:
        return Request(token=config.token, path=path)

    def parse_params(self, params: Dict[str, str]) -> Dict[str, str]:
        parsed = {}
        if params is not None:
            for key, value in params.items():
                if value:
                    parsed.update({key: value})
        return parsed

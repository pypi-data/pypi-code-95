#!/usr/bin/env python3

from json import dumps as json_dumps
from CloudflareAPI.core import CFBase


class User(CFBase):
    def __init__(self) -> None:
        self.request = self.get_request("user")

    def details(self, minimal: bool = True, formated=False):
        data = self.request.get()
        if minimal and "organizations" in data.keys():
            del data["organizations"]
        if formated:
            return json_dumps(data, indent=2)
        return data

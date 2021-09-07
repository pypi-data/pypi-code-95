#!/usr/bin/env python3

from re import match
from CloudflareAPI.core import CFBase, Request
from CloudflareAPI.exceptions import CFError


class Subdomain(CFBase):
    def __init__(self, account_id: str) -> None:
        self.account_id = account_id
        base_path = f"/accounts/{self.account_id}/workers/subdomain"
        self.request = self.get_request(base_path)

    def create(self, name: str) -> str:
        name = name.replace("_", "-").lower()
        if not match("^[a-z0-9]([a-z0-9-]{0,61}[a-z0-9])?$", name):
            raise CFError("Subdomain is not valid")
        return self.request.put(json=dict(subdomain=name))

    def get(self) -> str:
        return self.request.get()["subdomain"]

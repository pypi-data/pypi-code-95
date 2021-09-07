#!/usr/bin/env python3

from typing import Optional
from CloudflareAPI.core import CFBase
from CloudflareAPI.api import Account, Worker, Storage, User


class Cloudflare(CFBase):
    def __init__(self, bare: bool = False, account_id: Optional[str] = None) -> None:
        self.account = Account(account_id)
        self.user = User()
        if not bare:
            self.worker = self.get_worker()
            self.store = self.get_store()

    def get_worker(self) -> Worker:
        return Worker(account_id=self.account.id)

    def get_store(self) -> Storage:
        return Storage(account_id=self.account.id)

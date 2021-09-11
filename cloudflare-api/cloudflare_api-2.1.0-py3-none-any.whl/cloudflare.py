#!/usr/bin/env python3

from typing import Optional

from .core import CFBase
from .api import Account, Worker, Storage, User


class Cloudflare(CFBase):
    def __init__(
        self,
        token: Optional[str] = None,
        account_id: Optional[str] = None,
        bare: bool = False,
    ) -> None:
        self.validate(token)
        self.account = Account(account_id)
        self.user = User()
        if not bare:
            self.worker = self.get_worker()
            self.store = self.get_store()

    def get_worker(self) -> Worker:
        return Worker(account_id=self.account.id)

    def get_store(self) -> Storage:
        return Storage(account_id=self.account.id)

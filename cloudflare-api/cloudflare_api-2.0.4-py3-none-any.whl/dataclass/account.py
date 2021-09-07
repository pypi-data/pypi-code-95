#!/usr/bin/env python3

import json
from datetime import datetime
from dataclasses import dataclass
from typing import Optional


@dataclass
class AccountSettings:
    enforce_twofactor: bool
    access_approval_expiry: Optional[bool]
    use_account_custom_ns_by_default: bool

    def __repr__(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, indent=2)


@dataclass
class AccountData:
    id: str
    name: str
    settings: AccountSettings
    created_on: str

    @property
    def formated_created_on(self) -> datetime:
        return datetime.strptime(f"{self.created_on[:-1]}00", "%Y-%m-%dT%H:%M:%S.%f")

    def __repr__(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, indent=2)

    def __str__(self) -> str:
        return f"{self.name}: {self.id}"

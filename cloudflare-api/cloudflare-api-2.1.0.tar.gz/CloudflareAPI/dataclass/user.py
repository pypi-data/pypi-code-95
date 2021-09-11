#!/usr/bin/env python3

import json
from typing import Any, Dict
from datetime import datetime
from dataclasses import dataclass


@dataclass
class UserData:
    id: str
    email: str
    username: str
    first_name: str
    last_name: str
    telephone: str
    country: str
    zipcode: str
    two_factor_authentication_enabled: bool
    two_factor_authentication_locked: bool
    created_on: str
    modified_on: str
    has_pro_zones: bool
    has_business_zones: bool
    has_enterprise_zones: bool
    suspended: bool

    def __init__(self, data: Dict[str, Any]) -> None:
        for key in data:
            setattr(self, key, data[key])

    @property
    def formated_created_on(self) -> datetime:
        return datetime.strptime(f"{self.created_on[:-1]}00", "%Y-%m-%dT%H:%M:%S.%f")

    @property
    def formated_modified_on(self) -> datetime:
        return datetime.strptime(f"{self.modified_on[:-1]}00", "%Y-%m-%dT%H:%M:%S.%f")

    def __repr__(self) -> str:
        return json.dumps(self, default=lambda o: o.__dict__, indent=2)

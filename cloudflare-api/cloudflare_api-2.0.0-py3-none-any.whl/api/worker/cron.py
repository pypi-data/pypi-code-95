#!/usr/bin/env python3


from typing import Any, Dict, List
from CloudflareAPI.core import CFBase, Request


class Cron(CFBase):
    def __init__(self, account_id: str) -> None:
        self.account_id = account_id
        base_path = f"/accounts/{self.account_id}/workers/scripts"
        self.request = self.get_request(base_path)

    def update(self, worker: str, crons: List[str]) -> Any:
        crons = [{"cron": cron} for cron in crons]
        return self.request.put(f"/{worker}/schedules", json=crons)["schedules"]

    def get(self, worker: str) -> Any:
        return self.request.get(f"/{worker}/schedules")["schedules"]

#!/usr/bin/env python3

from json import dumps as json_dumps
from pathlib import Path
from typing import Any, Dict, List, Optional, Union
from CloudflareAPI.core import CFBase, Request
from CloudflareAPI.api.worker.cron import Cron
from CloudflareAPI.api.worker.subdomain import Subdomain


class Worker(CFBase):
    class Metadata:
        def __init__(self) -> None:
            self.data = dict(body_part="script", bindings=[])

        def __call__(self):
            return (None, json_dumps(self.data), "application/json")

        def _sanitize(self, text: str):
            return text.strip().replace(" ", "_").upper()

        def add_binding(self, name: str, namespace_id: str):
            binding = dict(
                name=self._sanitize(name),
                type="kv_namespace",
                namespace_id=namespace_id,
            )
            self.data["bindings"].append(binding)

        def add_variable(self, name: str, text: str):
            binding = dict(name=self._sanitize(name), type="plain_text", text=text)
            self.data["bindings"].append(binding)

        def add_secret(self, name: str, secret: str):
            binding = dict(name=self._sanitize(name), type="secret_text", text=secret)
            self.data["bindings"].append(binding)

        def __repr__(self) -> str:
            return json_dumps(self.data, indent=2)

    def __init__(self, account_id: str) -> None:
        self.account_id = account_id
        base_path = f"/accounts/{self.account_id}/workers/scripts"
        self.request = self.get_request(base_path)
        self.cron = Cron(self.account_id)
        self.subdomain = Subdomain(self.account_id)

    def list(
        self,
        detailed: bool = False,
        params: Optional[Dict[str, Any]] = None,
        formated: bool = False,
    ) -> List:
        workers = self.request.get(params=params)
        if detailed:
            wlist = [
                {
                    worker["id"]: [
                        {item["script"]: item["pattern"]} for item in worker["routes"]
                    ]
                }
                if worker["routes"] is not None
                else {worker["id"]: "No routes"}
                for worker in workers
            ]
        else:
            wlist = [worker["id"] for worker in workers]
        if formated:
            return json_dumps(wlist, indent=2)
        return wlist

    def download(self, name: str, directory: str = "./workers") -> int:

        data = self.request.get(name)
        directory = Path(directory)
        directory.mkdir(parents=True, exist_ok=True)
        directory.resolve(strict=True)
        file = directory / f"{name}.js"
        return file.write_text(data)

    def upload(self, name: str, file: str, metadata: Optional[Metadata] = None) -> Any:
        file = Path(file)
        file.resolve(strict=True)
        if metadata is None:
            data = file.read_text()
            return self.request.put(
                name, data=data, headers={"Content-Type": "application/javascript"}
            )
        miltipart_data = {
            "metadata": metadata(),
            "script": (
                file.name,
                file.open("rb"),
                "application/javascript",
            ),
        }
        return self.request.put(name, files=miltipart_data)

    def deploy(self, name: str) -> bool:
        return self.request.post(f"{name}/subdomain", json={"enabled": True})

    def undeploy(self, name: str) -> bool:
        return self.request.post(f"{name}/subdomain", json={"enabled": False})

    def delete(self, name: str) -> bool:
        return self.request.delete(name)

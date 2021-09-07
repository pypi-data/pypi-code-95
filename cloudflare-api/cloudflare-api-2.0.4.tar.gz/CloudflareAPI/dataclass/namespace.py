#!/usr/bin/env python3


import json
from typing import Dict, List, Optional, Union
from CloudflareAPI.core import CFBase


class Namespace(CFBase):
    id: str
    title: str
    supports_url_encoding: bool

    class Metadata:
        def __init__(self, key: Union[str, "Namespace.NSKey"], value: str) -> None:
            if not isinstance(key, str):
                key = key.name
            self.data = {key.strip(): value}

        def __call__(self) -> Dict[str, str]:
            return (None, json.dumps(self.data), "application/json")

    class NSKey:
        def __init__(self, key: Dict[str, str]) -> None:
            self.name = key["name"]
            if "expiration" in key:
                self.expiration = key["expiration"]
            if "metadata" in key:
                self.metadata = key["metadata"]

        def __repr__(self) -> str:
            return json.dumps(self.__dict__, indent=2)

        def __str__(self) -> str:
            return self.name

    class NSBundler:
        def __init__(self) -> None:
            self.list = []

        def add(
            self,
            key: str,
            value: str,
            expiration: Optional[int] = None,
            expiration_ttl: Optional[int] = None,
            metadata: Optional["Namespace.Metadata"] = None,
            base64: Optional[bool] = None,
        ) -> None:
            data = {
                "key": key.strip(),
                "value": value,
            }
            if metadata is not None:
                data.update({"metadata": metadata.data})
            params = {
                "expiration": expiration,
                "expiration_ttl": expiration_ttl,
                "base64": base64,
            }
            for pkey, pvalue in params.items():
                if params[pkey] is not None:
                    data.update({pkey: pvalue})
            self.list.append(data)

    def __init__(self, account_id, data) -> None:
        self.id = data["id"]
        self.title = data["title"]
        self.supports_url_encoding = data["supports_url_encoding"]
        base_path = f"/accounts/{account_id}/storage/kv/namespaces/{self.id}"
        self.request = self.get_request(base_path)
        super().__init__()

    def keys(
        self,
        limit: Optional[int] = None,
        cursor: Optional[str] = None,
        prefix: Optional[str] = None,
    ) -> List[Dict[str, str]]:
        params = {"limit": limit, "cursor": cursor, "prefix": prefix}
        params = self.parse_params(params)
        data = self.request.get("keys", params=params)
        keys = [self.NSKey(key) for key in data]
        return keys

    def read(self, key: Union[str, NSKey]) -> str:
        if not isinstance(key, str):
            key = key.name
        return self.request.get(f"values/{key}")

    def write(
        self,
        key: Union[str, NSKey],
        value: str,
        metadata: Optional[Metadata] = None,
        expiration: Optional[str] = None,
        expiration_ttl: Optional[int] = None,
    ) -> bool:
        if not isinstance(key, str):
            key = key.name
        params = {"expiration": expiration, "expiration_ttl": expiration_ttl}
        params = self.parse_params(params)
        if metadata is None:
            headers = {"Content-Type": "text/plain"}
            return self.request.put(
                f"values/{key}", data=value, params=params, headers=headers
            )
        miltipart_data = {
            "metadata": metadata(),
            "value": value,
        }
        return self.request.put(f"values/{key}", files=miltipart_data)

    def bulk_write(self, bundle: NSBundler) -> bool:
        return self.request.put("bulk", json=bundle.list)

    def delete(self, key: Union[str, NSKey]) -> bool:
        if not isinstance(key, str):
            key = key.name
        return self.request.delete(f"values/{key}")

    def bulk_delete(self, keys: List[Union[str, NSKey]]) -> bool:
        keyList: List[str] = []
        for key in keys:
            if not isinstance(key, str):
                keyList.append(key.name)
            keyList.append(key)
        return self.request.delete("bulk", json=keyList)

    def __repr__(self) -> str:
        return json.dumps(
            {
                "id": self.id,
                "title": self.title,
                "supports_url_encoding": self.supports_url_encoding,
            },
            indent=2,
        )

    def __str__(self) -> str:
        return f"{self.title}: {self.id}"

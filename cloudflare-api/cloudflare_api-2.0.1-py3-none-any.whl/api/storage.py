#!/usr/bin/env python3

from typing import Any, Dict, List, Optional
from CloudflareAPI.core import CFBase
from CloudflareAPI.exceptions import CFError
from CloudflareAPI.dataclass.namespace import Namespace


class Storage(CFBase):
    def __init__(self, account_id: str) -> None:
        self.account_id = account_id
        base_path = f"/accounts/{self.account_id}/storage/kv/namespaces"
        self.request = self.get_request(base_path)

    def list(
        self,
        params: Optional[Dict[str, Any]] = None,
    ) -> Any:
        params = self.parse_params(params)
        stores = self.request.get(params=params)
        stores = [Namespace(self.account_id, ns) for ns in stores]
        self._stores = stores
        return stores

    def get_ns(self, namespace: str) -> Namespace:
        stores = self.list()
        namespace = namespace.upper()
        for store in stores:
            if namespace == store.title:
                return store
        raise CFError("Namespace not found")

    def create(self, namespace: str) -> bool:
        namespace = namespace.upper()
        result = self.request.post(json=dict(title=namespace))
        if result["title"] == namespace:
            return result["id"]
        raise CFError("Unable to create namespace")

    def rename(self, old_namespace: str, new_namespace: str):
        old_namespace = old_namespace.upper()
        new_namespace = new_namespace.upper()
        store = self.get_ns(old_namespace)
        return self.request.put(store.id, json={"title": new_namespace})

    def delete(self, namespace: str):
        namespace = namespace.upper()
        store = self.get_ns(namespace)
        return self.request.delete(store.id)

from __future__ import annotations

from dataclasses import dataclass, field
from typing import TypeVar, Generic, MutableMapping, Callable, Tuple


T = TypeVar("T")


@dataclass
class Node(Generic[T]):
    value: T
    children: MutableMapping[str, "Node"] = field(default_factory=dict)

    def put(self, path: Tuple[str, ...], fn: Callable[[T, Tuple[str, ...]], T]) -> Node:
        if not path:
            return self
        if path[0] in self.children:
            return self.children[path[0]].put(path[1:], fn)  # type: ignore
        node = Node(value=fn(self.value, path))
        self.children[path[0]] = node
        return node.put(path[1:], fn)  # type: ignore
